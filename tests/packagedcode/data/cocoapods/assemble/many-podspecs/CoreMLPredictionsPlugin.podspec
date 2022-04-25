# Version definitions
$AMPLIFY_VERSION = '1.23.0'
$AMPLIFY_RELEASE_TAG = "v#{$AMPLIFY_VERSION}"

Pod::Spec.new do |s|
  s.name         = 'CoreMLPredictionsPlugin'

  s.version      = $AMPLIFY_VERSION
  s.summary      = 'Amazon Web Services Amplify for iOS.'

  s.description  = 'AWS Amplify for iOS provides a declarative library for application development using cloud services'

  s.homepage     = 'https://github.com/aws-amplify/amplify-ios'
  s.license      = 'Apache License, Version 2.0'
  s.author       = { 'Amazon Web Services' => 'amazonwebservices' }
  s.source       = { :git => 'https://github.com/aws-amplify/amplify-ios.git', :tag => $AMPLIFY_RELEASE_TAG }

  s.platform     = :ios, '13.0'
  s.swift_version = '5.0'

  s.source_files = 'AmplifyPlugins/Predictions/CoreMLPredictionsPlugin/**/*.swift'

  s.dependency 'Amplify', $AMPLIFY_VERSION

end
