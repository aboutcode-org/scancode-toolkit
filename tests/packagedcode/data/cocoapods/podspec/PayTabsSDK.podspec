Pod::Spec.new do |s|
  s.name         = "PayTabsSDK"
  s.version      = "6.1.18"
  s.summary      = "PayTabs is an online payment gateway."
  s.ios.deployment_target = '10.0'
  s.homepage     = "https://github.com/paytabscom/paytabs-ios-library-sample/tree/master"
  s.license      = "MIT"
  s.author       = { "PayTabs" => "m.adly@paytabs.com" }
  s.source   = { :git => 'https://github.com/paytabscom/paytabs-ios-library-sample.git', :tag => s.version.to_s }
  s.frameworks = 'Foundation', 'CoreTelephony', 'WebKit', 'PassKit', 'SystemConfiguration', 'CoreLocation'
  s.swift_version = '5.0'
  s.ios.vendored_frameworks = 'sources/PaymentSDK.xcframework'
  s.xcconfig = { 'FRAMEWORK_SEARCH_PATHS' => "'${PODS_ROOT}'/sources/**", 'SWIFT_INCLUDE_PATHS' => "'${PODS_TARGET_SRCROOT}'/sources/**"}

end
