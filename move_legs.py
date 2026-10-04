import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist
import math

class MoveLegsNode(Node):
    def __init__(self):
        super().__init__('move_legs_node')
        self.publisher_ = self.create_publisher(Float64MultiArray, '/leg_controller/commands', 10)
        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.timer = self.create_timer(0.02, self.timer_callback)

        self.counter = 0.0
        self.current_pos = [0.0] * 8

        self.linear_x = 0.0
        self.angular_z = 0.0
        self.is_moving = False
        
        # STABILITY FIX: Slower gait speed allows Gazebo physics to "catch" the feet
        self.gait_speed = 0.02 

    def cmd_vel_callback(self, msg):
        self.linear_x = msg.linear.x
        self.angular_z = msg.angular.z
        self.is_moving = abs(self.linear_x) > 0.01 or abs(self.angular_z) > 0.01

    def timer_callback(self):
        msg = Float64MultiArray()

        if not self.is_moving:
            for i in range(8):
                self.current_pos[i] += (0.0 - self.current_pos[i]) * 0.1
            msg.data = self.current_pos
            self.publisher_.publish(msg)
            return

        linear = max(-1.0, min(self.linear_x, 1.0))
        angular = max(-0.8, min(self.angular_z, 0.8))

        effective_speed = max(abs(linear), abs(angular) * 0.3)
        effective_speed = max(0.3, min(effective_speed, 1.2))
        self.counter += self.gait_speed * effective_speed

        # STABILITY FIX: Higher amplitude (1.8) and deeper push (0.6) 
        # This forces the legs to dig into the ground rather than "ice-skate"
        def smooth_gait(p, amplitude=1.8):
            val = math.sin(p)
            # STANCE PHASE (Pushing): Stay on ground longer and push deeper
            if val < 0:
                return amplitude * (val * 0.75) # Dig into the floor
            # SWING PHASE (Resetting): Lift higher to ensure no dragging
            else:
                return amplitude * (val * 0.3)

        phase_offset = 0.0 if linear >= 0 else math.pi

        fl_phase = self.counter + phase_offset
        fr_phase = self.counter + math.pi + phase_offset
        bl_phase = self.counter + math.pi + phase_offset
        br_phase = self.counter + phase_offset

        hip_lean = angular * 0.12 # Slightly more lean for better turn authority
        hip_lean = max(-0.25, min(hip_lean, 0.25))

        target_pos = [
            -hip_lean, smooth_gait(fl_phase), # FL
            -hip_lean, smooth_gait(fr_phase), # FR
            hip_lean,  smooth_gait(bl_phase), # BL
            hip_lean,  smooth_gait(br_phase), # BR
        ]

        # STABILITY FIX: filter_alpha 0.1 prevents the "snapping" jitter
        filter_alpha = 0.1 
        for i in range(8):
            self.current_pos[i] += (target_pos[i] - self.current_pos[i]) * filter_alpha

        msg.data = self.current_pos
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MoveLegsNode()
    try:
        rclpy.spin(node)
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
