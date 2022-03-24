Pod::Spec.new do |spec|
  spec.name = 'kmmWebSocket'
  spec.version = '1.0.1'
  spec.homepage = 'https://www.cocoapods.org'
  spec.source = { :git => "Not Published", :tag => "#{spec.version}" }
  spec.authors = 'Ahmed Ibrahim'
  spec.license = { :type => "MIT", :file => "LICENSE" }
  spec.summary = 'A Kotlin Multiplatform WebSocket Library'
  spec.static_framework = true
  spec.vendored_frameworks = "kmmWebSocket.xcframework"
  spec.libraries = "c++"
  spec.module_name = "#{spec.name}_umbrella"
  spec.ios.deployment_target = '11.0'
end

# path -> build/XCFrameworks/release