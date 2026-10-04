import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import math

class QuadrupedGait(Node):
    def __init__(self):
        super().__init__('quadruped_gait')
        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.publisher_ = self.create_publisher(Float64MultiArray, '/leg_controller/commands', 10)
        
        # Increased to 50Hz (0.02s) for smoother command streaming
        self.timer = self.create_timer(0.02, self.gait_loop)
        
        self.linear_vel = 0.0
        self.yaw_rate = 0.0
        self.counter = 0.0

    def cmd_callback(self, msg):
        self.linear_vel = msg.linear.x
        self.yaw_rate = msg.angular.z

    def gait_loop(self):
        msg = Float64MultiArray()
        
        if abs(self.linear_vel) > 0.01 or abs(self.yaw_rate) > 0.01:
            # Slower increment (0.1) prevents the "jerk" that causes wobbling
            self.counter += 0.1 
            
            # Lower swing amplitude for a more grounded "shuffle"
            base_swing = 0.4 * self.linear_vel
            
            # Steering multipliers
            l_mult = 1.0 - (self.yaw_rate * 0.4)
            r_mult = 1.0 + (self.yaw_rate * 0.4)
            
            # Diagonal pairs
            # Pair 1: FL and BR
            # Pair 2: FR and BL
            phase_a = math.sin(self.counter)
            phase_b = math.sin(self.counter + math.pi)
            
            fl = base_swing * phase_a * l_mult
            br = base_swing * phase_a * r_mult
            fr = base_swing * phase_b * r_mult
            bl = base_swing * phase_b * l_mult
            
            msg.data = [float(fl), float(fr), float(bl), float(br)]
        else:
            # Neutral standing position
            msg.data = [0.0, 0.0, 0.0, 0.0]
            self.counter = 0.0
            
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = QuadrupedGait()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
