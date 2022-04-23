#
#  Be sure to run `pod spec lint Amplify.podspec' to ensure this is a
#  valid spec and to remove all comments including this before submitting the spec.
#
#  To learn more about Podspec attributes see https://guides.cocoapods.org/syntax/podspec.html
#  To see working Podspecs in the CocoaPods repo see https://github.com/CocoaPods/Specs/
#

# Version definitions
$AMPLIFY_VERSION = '1.23.0'
$AMPLIFY_RELEASE_TAG = "v#{$AMPLIFY_VERSION}"

Pod::Spec.new do |s|
  s.name         = 'Amplify'
  s.version      = $AMPLIFY_VERSION
  s.summary      = 'Amazon Web Services Amplify for iOS.'

  s.description  = 'AWS Amplify for iOS provides a declarative library for application development using cloud services'

  s.homepage     = 'https://github.com/aws-amplify/amplify-ios'
  s.license      = 'Apache License, Version 2.0'
  s.author       = { 'Amazon Web Services' => 'amazonwebservices' }
  s.source       = { :git => 'https://github.com/aws-amplify/amplify-ios.git', :tag => $AMPLIFY_RELEASE_TAG }

  s.platform     = :ios, '11.0'
  s.swift_version = '5.0'

  s.source_files = 'Amplify/**/*.swift'
  s.default_subspec = 'Default'

  # There appears to be a bug in Xcode < 12 where SwiftUI isn't properly
  # weak-linked even though system frameworks should be weak-linked by default.
  # Explicitly weak link it here until we upgrade Amplify's platform support
  # version to >= 13.0. https://github.com/aws-amplify/amplify-ios/issues/878
  s.weak_frameworks = 'SwiftUI'

  s.subspec 'Default' do |default|
    default.preserve_path = 'AmplifyTools'
    default.script_phase = {
      :name => 'Default',
      :script => 'echo "no-op"',
      :execution_position => :before_compile
    }
  end

  s.subspec 'Tools' do |ss|
    ss.preserve_path = 'AmplifyTools'
    ss.script_phase = {
      :name => 'AmplifyTools',
      :script => 'mkdir -p "${PODS_ROOT}/AmplifyTools"; cp -vf "${PODS_TARGET_SRCROOT}/AmplifyTools/amplify-tools.sh" "${PODS_ROOT}/AmplifyTools/."',
      :execution_position => :before_compile
    }
  end

end
