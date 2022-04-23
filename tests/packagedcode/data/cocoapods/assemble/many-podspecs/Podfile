load 'build-support/dependencies.rb'

platform :ios, "11.0"

target "Amplify" do
  # Comment the next line if you"re not using Swift and don"t want to use dynamic frameworks
  use_frameworks!

  include_build_tools!

  abstract_target "AmplifyTestConfigs" do
    include_test_utilities!
    
    target "AmplifyTestCommon" do
      pod "AWSCore", $OPTIMISTIC_AWS_SDK_VERSION
    end

    target "AmplifyTests" do
    end

    target "AmplifyFunctionalTests" do
    end

  end

  target "AWSPluginsCore" do
    inherit! :complete
    use_frameworks!

    pod "AWSCore", $OPTIMISTIC_AWS_SDK_VERSION

    abstract_target "AWSPluginsTestConfigs" do
      include_test_utilities!

      target "AWSPluginsCoreTests" do
      end

      target "AWSPluginsTestCommon" do
      end
    end

  end

end

target "AmplifyTestApp" do
  use_frameworks!
  include_test_utilities!
end
