#
# Be sure to run `pod lib lint LoadingShimmer.podspec' to ensure this is a
# valid spec before submitting.
#
# Any lines starting with a # are optional, but their use is encouraged
# To learn more about a Podspec see https://guides.cocoapods.org/syntax/podspec.html
#

Pod::Spec.new do |s|
  s.name             = 'LoadingShimmer'
  s.version          = '1.0.3'
  s.summary          = 'An easy way to add a shimmering effect to any view with just one line of code. It is useful as an unobtrusive loading indicator.'

  s.description      = <<-DESC
  An easy way to add a shimmering effect to any view with just single line of code. It is useful as an unobtrusive loading indicator. This is a network request waiting for the framework, the framework to increase the dynamic effect, convenient and fast, a line of code can be used.
                       DESC

  s.homepage         = 'https://github.com/jogendra/LoadingShimmer'
  # s.screenshots     = 'https://github.com/jogendra/LoadingShimmer/blob/master/Screenshots/demo.png', 'https://github.com/jogendra/LoadingShimmer/blob/master/Screenshots/shimmer.png'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.author           = { 'jogendra' => 'jogendrafx@gmail.com' }
  s.source           = { :git => 'https://github.com/jogendra/LoadingShimmer.git', :tag => s.version.to_s }
  s.social_media_url = 'https://twitter.com/jogendrafx'

  s.ios.deployment_target = '10.0'
  s.swift_version = '5.0'

  s.source_files = 'LoadingShimmer/Classes/**/*'
  
  # s.resource_bundles = {
  #   'LoadingShimmer' => ['LoadingShimmer/Assets/*.png']
  # }

  # s.public_header_files = 'Pod/Classes/**/*.h'
  # s.frameworks = 'UIKit', 'MapKit'
  # s.dependency 'AFNetworking', '~> 2.3'
end
