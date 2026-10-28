require 'xcodeproj'

root = File.expand_path(__dir__)
project = Xcodeproj::Project.new(File.join(root, 'BecomeSwiftUIDemo.xcodeproj'))
project.root_object.attributes['LastUpgradeCheck'] = '2700'
target = project.new_target(:application, 'BecomeSwiftUIDemo', :ios, '16.0')
target.product_reference.name = 'BecomeSwiftUIDemo.app'

app = project.main_group.new_group('App', 'App')
%w[AppDelegate.swift SceneDelegate.swift BecomeSwiftUIScreen.swift BecomeSDKBridge.swift].each do |name|
  target.source_build_phase.add_file_reference(app.new_file(name))
end
app.new_file('Info.plist')
%w[Secrets.plist com.become.document.key.txt].each do |name|
  next unless File.file?(File.join(root, 'App', name))

  target.resources_build_phase.add_file_reference(app.new_file(name))
end

{
  'Localizable.strings' => %w[en es es-419],
  'InfoPlist.strings' => %w[es es-419]
}.each do |name, locales|
  group = app.new_variant_group(name)
  locales.each do |locale|
    ref = group.new_file("#{locale}.lproj/#{name}")
    ref.name = locale
  end
  target.resources_build_phase.add_file_reference(group)
end

frameworks = project.main_group.new_group('Frameworks')
framework = frameworks.new_file('../../BDIdentityVerification.xcframework')
target.frameworks_build_phase.add_file_reference(framework)
embed = target.new_copy_files_build_phase('Embed Frameworks')
embed.dst_subfolder_spec = '10'
embed_file = embed.add_file_reference(framework)
embed_file.settings = { 'ATTRIBUTES' => %w[CodeSignOnCopy RemoveHeadersOnCopy] }

packages = {
  'https://github.com/aws-amplify/amplify-swift' => ['2.53.3', 'Amplify'],
  'https://github.com/aws-amplify/amplify-ui-swift-liveness' => ['1.4.4', 'FaceLiveness'],
  'https://github.com/BlinkID/capture-core-sp' => ['1.4.3', 'CaptureCore'],
  'https://github.com/BlinkID/capture-ux-sp' => ['1.4.3', 'CaptureUX']
}
packages.each do |url, (version, product_name)|
  reference = project.new(Xcodeproj::Project::Object::XCRemoteSwiftPackageReference)
  reference.repositoryURL = url
  reference.requirement = { 'kind' => 'exactVersion', 'version' => version }
  project.root_object.package_references << reference
  product = project.new(Xcodeproj::Project::Object::XCSwiftPackageProductDependency)
  product.package = reference
  product.product_name = product_name
  target.package_product_dependencies << product
  build_file = project.new(Xcodeproj::Project::Object::PBXBuildFile)
  build_file.product_ref = product
  target.frameworks_build_phase.files << build_file
end

target.build_configurations.each do |configuration|
  configuration.build_settings.merge!({
    'PRODUCT_BUNDLE_IDENTIFIER' => ENV.fetch('BECOME_DEMO_BUNDLE_ID', 'com.example.become.legacy.demo'),
    'INFOPLIST_FILE' => 'App/Info.plist',
    'GENERATE_INFOPLIST_FILE' => 'NO',
    'SWIFT_VERSION' => '5.0',
    'TARGETED_DEVICE_FAMILY' => '1',
    'IPHONEOS_DEPLOYMENT_TARGET' => '16.0',
    'CODE_SIGN_STYLE' => 'Automatic',
    'ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES' => 'YES'
  })
end
project.save
