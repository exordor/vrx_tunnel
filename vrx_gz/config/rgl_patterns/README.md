Put your RGL lidar pattern preset files here (e.g. *.mat3x4f).

Example YAML usage (in any package):

  pattern_preset_path: $(find vrx_gz)/config/rgl_patterns/hesai_qt128_20hz_pattern.mat3x4f

Notes:
- Ensure this file exists after build under install/share/vrx_gz/config/rgl_patterns/.
- This path is portable across machines that have the package installed.
