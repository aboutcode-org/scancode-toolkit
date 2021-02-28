module github.com/census-instrumentation/opencensus-service

require (
	contrib.go.opencensus.io v0.0.0-20181029163544-2befc13012d0
	gopkg.in/yaml.v2 v2.2.5
)

replace git.apache.org/thrift.git => github.com/apache/thrift v0.12.0

go 1.13