#
# To learn more about a Podspec see http://guides.cocoapods.org/syntax/podspec.html.
# Run pod lib lint flutter_paytabs_bridge.podspec' to validate before publishing.
#
Pod::Spec.new do |s|
  s.name             = 'flutter_paytabs_bridge'
  s.version          = '2.2.5'
  s.summary          = 'A new flutter plugin project.'
  s.description      = <<-DESC
A new flutter plugin project.
                       DESC
  s.homepage         = 'http://example.com'
  s.license          = { :file => '../LICENSE' }
  s.author           = { 'Your Company' => 'email@example.com' }
  s.source           = { :path => '.' }
  s.source_files = 'Classes/**/*'
  s.dependency 'Flutter'
  s.platform = :ios, '10.0'
  s.dependency "PayTabsSDK", "6.1.18"
  s.static_framework = true
  # Flutter.framework does not contain a i386 slice.
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES', 'EXCLUDED_ARCHS[sdk=iphonesimulator*]' => 'i386' }
  s.swift_version = '5.0'
end
