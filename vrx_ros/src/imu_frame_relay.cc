/*
 * Simple IMU frame_id rewriter: subscribes to sensor_msgs/Imu, replaces
 * header.frame_id with a desired frame (default: parent of incoming frame),
 * and republishes.
 */

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>

#include <string>

class ImuFrameRelay : public rclcpp::Node {
public:
  ImuFrameRelay() : Node("imu_frame_relay") {
    this->declare_parameter<std::string>("input", "sensors/imu/imu/data");
    this->declare_parameter<std::string>("output", "sensors/imu/data");
    this->declare_parameter<std::string>("frame_id", "");

    auto in = this->get_parameter("input").as_string();
    auto out = this->get_parameter("output").as_string();

    pub_ = this->create_publisher<sensor_msgs::msg::Imu>(out, rclcpp::SensorDataQoS());
    sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
        in, rclcpp::SensorDataQoS(),
        std::bind(&ImuFrameRelay::OnImu, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "Relaying IMU from '%s' to '%s'", in.c_str(), out.c_str());
  }

private:
  static std::string Normalize(const std::string &in)
  {
    if (in.empty()) return in;
    std::stringstream ss(in);
    std::string tok; std::vector<std::string> parts;
    while (std::getline(ss, tok, '/'))
    {
      if (tok.empty()) continue;
      if (!parts.empty() && parts.back() == tok) continue; // collapse dup tokens
      parts.push_back(tok);
    }
    std::ostringstream out;
    for (size_t i = 0; i < parts.size(); ++i)
    {
      if (i) out << "/";
      out << parts[i];
    }
    return out.str();
  }

  std::string ParentFrame(const std::string &frame) {
    auto pos = frame.rfind('/');
    if (pos == std::string::npos) return frame;
    return frame.substr(0, pos);
  }

  void OnImu(const sensor_msgs::msg::Imu::SharedPtr msg) {
    auto out = *msg;
    auto desired = this->get_parameter("frame_id").as_string();
    if (desired.empty())
      desired = ParentFrame(out.header.frame_id);
    out.header.frame_id = Normalize(desired);
    pub_->publish(out);
  }

  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr pub_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr sub_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ImuFrameRelay>());
  rclcpp::shutdown();
  return 0;
}
