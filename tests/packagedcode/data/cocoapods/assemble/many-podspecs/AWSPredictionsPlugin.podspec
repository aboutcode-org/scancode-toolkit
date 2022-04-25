# Version definitions
$AMPLIFY_VERSION = '1.23.0'
$AMPLIFY_RELEASE_TAG = "v#{$AMPLIFY_VERSION}"

$AWS_SDK_VERSION = '2.27.0'
$OPTIMISTIC_AWS_SDK_VERSION = "~> #{$AWS_SDK_VERSION}"

Pod::Spec.new do |s|
  s.name         = 'AWSPredictionsPlugin'

  s.version      = $AMPLIFY_VERSION
  s.summary      = 'Amazon Web Services Amplify for iOS.'

  s.description  = 'AWS Amplify for iOS provides a declarative library for application development using cloud services'

  s.homepage     = 'https://github.com/aws-amplify/amplify-ios'
  s.license      = 'Apache License, Version 2.0'
  s.author       = { 'Amazon Web Services' => 'amazonwebservices' }
  s.source       = { :git => 'https://github.com/aws-amplify/amplify-ios.git', :tag => $AMPLIFY_RELEASE_TAG }

  s.platform     = :ios, '13.0'
  s.swift_version = '5.0'

  s.source_files = 'AmplifyPlugins/Predictions/AWSPredictionsPlugin/**/*.swift'

  s.dependency 'AWSComprehend', $OPTIMISTIC_AWS_SDK_VERSION
  s.dependency 'AWSPluginsCore', $AMPLIFY_VERSION
  s.dependency 'AWSPolly', $OPTIMISTIC_AWS_SDK_VERSION
  s.dependency 'AWSRekognition', $OPTIMISTIC_AWS_SDK_VERSION
  s.dependency 'AWSTextract', $OPTIMISTIC_AWS_SDK_VERSION
  s.dependency 'AWSTranscribeStreaming', $OPTIMISTIC_AWS_SDK_VERSION
  s.dependency 'AWSTranslate', $OPTIMISTIC_AWS_SDK_VERSION
  s.dependency 'CoreMLPredictionsPlugin', $AMPLIFY_VERSION

  # This is technically redundant, but adding it here allows Xcode to find it
  # during initial indexing and prevent build errors after a fresh install
  s.dependency 'AWSCore', $OPTIMISTIC_AWS_SDK_VERSION

end
