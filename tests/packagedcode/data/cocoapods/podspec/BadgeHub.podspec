#
# Be sure to run `pod lib lint BadgeHub.podspec' to ensure this is a
# valid spec before submitting.
#
# Any lines starting with a # are optional, but their use is encouraged
# To learn more about a Podspec see https://guides.cocoapods.org/syntax/podspec.html
#

Pod::Spec.new do |s|
  s.name             = 'BadgeHub'
  s.version          = '0.1.1'
  s.summary          = 'A way to quickly add a notification bedge icon to any view.'

# This description is used to generate tags and improve search results.
#   * Think: What does it do? Why did you write it? What is the focus?
#   * Try to keep it short, snappy and to the point.
#   * Write the description between the DESC delimiters below.
#   * Finally, don't worry about the indent, CocoaPods strips it!

  s.description      = <<-DESC
Make any UIView a full fledged animated notification center. It is a way to quickly add a notification badge icon to a UIView. It make very easy to add badge to any view.
                       DESC

  s.homepage         = 'https://github.com/jogendra/BadgeHub'
  # s.screenshots     = 'www.example.com/screenshots_1', 'www.example.com/screenshots_2'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.author           = { 'jogendra' => 'imjog24@gmail.com' }
  s.source           = { :git => 'https://github.com/jogendra/BadgeHub.git', :tag => s.version.to_s }
  s.social_media_url = 'https://twitter.com/jogendrafx'

  s.ios.deployment_target = '10.0'
  s.swift_version = '5.0'

  s.source_files = 'BadgeHub/Classes/**/*'
  
  # s.resource_bundles = {
  #   'BadgeHub' => ['BadgeHub/Assets/*.png']
  # }

  # s.public_header_files = 'Pod/Classes/**/*.h'
  s.frameworks = 'UIKit', 'QuartzCore'
  # s.dependency 'AFNetworking', '~> 2.3'
end
