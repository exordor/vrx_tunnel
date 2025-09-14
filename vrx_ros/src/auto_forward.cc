/*
 Simple auto-forward controller for WAM-V.
 Publishes constant thrust to left/right thrusters.
*/

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64.hpp>

class AutoForward : public rclcpp::Node {
public:
  AutoForward() : Node("auto_forward") {
    this->declare_parameter<double>("thrust", 15.0);   // nominal thrust
    this->declare_parameter<double>("bias", 0.0);      // differential bias (+right, -left)
    this->declare_parameter<double>("rate_hz", 10.0);
    this->declare_parameter<double>("duration_sec", 0.0); // 0 => run forever

    double rate = this->get_parameter("rate_hz").as_double();
    left_pub_ = this->create_publisher<std_msgs::msg::Float64>("thrusters/left/thrust", 10);
    right_pub_ = this->create_publisher<std_msgs::msg::Float64>("thrusters/right/thrust", 10);

    start_time_ = this->now();
    timer_ = this->create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::duration<double>(1.0 / std::max(1e-3, rate))),
        std::bind(&AutoForward::OnTimer, this));
  }

private:
  void OnTimer() {
    const double duration = this->get_parameter("duration_sec").as_double();
    if (duration > 0.0 && (this->now() - start_time_).seconds() >= duration) {
      if (!stopped_) {
        // publish zero once to stop the vehicle and mark as stopped
        std_msgs::msg::Float64 z; z.data = 0.0;
        left_pub_->publish(z);
        right_pub_->publish(z);
        stopped_ = true;
      }
      return;
    }
    const double thrust = this->get_parameter("thrust").as_double();
    const double bias = this->get_parameter("bias").as_double();

    std_msgs::msg::Float64 left;  left.data = thrust - bias;
    std_msgs::msg::Float64 right; right.data = thrust + bias;
    left_pub_->publish(left);
    right_pub_->publish(right);
  }

  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr left_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr right_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Time start_time_;
  bool stopped_ {false};
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<AutoForward>());
  rclcpp::shutdown();
  return 0;
}
