module github.com/milvus-io/milvus

go 1.20

require github.com/apache/arrow/go/v12 v12.0.1

require github.com/milvus-io/milvus-storage/go v0.0.0-20231227072638-ebd0b8e56d70

require (
	github.com/go-playground/validator/v10 v10.14.0
	github.com/quasilyte/go-ruleguard/dsl v0.3.22
	golang.org/x/net v0.19.0
)

replace (
	github.com/apache/pulsar-client-go => github.com/milvus-io/pulsar-client-go v0.6.10
	github.com/bketelsen/crypt v0.0.3 => github.com/bketelsen/crypt v0.0.4 // Fix security alert for core-os/etcd
	github.com/expr-lang/expr => github.com/SimFG/expr v0.0.0-20231218130003-94d085776dc5
	github.com/milvus-io/milvus/pkg => ./pkg
)

replace github.com/streamnative/pulsarctl => github.com/xiaofan-luan/pulsarctl v0.5.1

exclude github.com/apache/pulsar-client-go/oauth2 v0.0.0-20211108044248-fe3b7c4e445b
