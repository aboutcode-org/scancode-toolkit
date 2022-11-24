Pod::Spec.new do |s|
  s.name             = "Artsy+UIFonts"
  s.version          = "3.3.4"
  s.summary          = "The open source fonts for Artsy apps + UIFont categories."
  s.homepage         = "https://github.com/artsy/Artsy-OSSUIFonts"
  s.license          = 'Code is MIT, then custom font licenses.'
  s.author           = { "Orta" => "orta@artsymail.com" }
  s.source           = { :git => "https://github.com/artsy/Artsy-OSSUIFonts.git", :tag => s.version }
  s.social_media_url = 'https://twitter.com/artsyopensource'

  s.ios.deployment_target = '8.0'
  s.tvos.deployment_target = '9.0'

  s.source_files = 'Pod/Classes'
  s.resources = 'Pod/Assets/*'
  s.preserve_paths = 'Pod/Scripts/*'

  s.frameworks = 'UIKit', 'CoreText'
  s.prepare_command = "./Pod/Scripts/ArtsySetup.rb"
end
