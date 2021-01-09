package utils

import (
	"io"
	"time"

	"github.com/opentracing/opentracing-go"

	"github.com/uber/jaeger-client-go/config"
)

func getTracer(jaegerHostPort string, serviceName string) (opentracing.Tracer, io.Closer, error) {

	cfg := config.Configuration{
		Sampler: &config.SamplerConfig{
			Type:  "const",
			Param: 1,
		},
		Reporter: &config.ReporterConfig{
			LogSpans:            false,
			BufferFlushInterval: 1 * time.Second,
			LocalAgentHostPort:  jaegerHostPort,
		},
	}
	return cfg.New(
		serviceName,
	)
}
