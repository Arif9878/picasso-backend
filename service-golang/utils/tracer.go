package utils

import (
	"io"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/opentracing/opentracing-go"
	"github.com/uber/jaeger-client-go/config"
)

func GetJaegerTracer(JaegerHostPort string, ServiceName string) (opentracing.Tracer, io.Closer, error) {

	cfg := config.Configuration{
		ServiceName: ServiceName,
		Sampler: &config.SamplerConfig{
			Type:  "const",
			Param: 1,
		},
		Reporter: &config.ReporterConfig{
			LogSpans:            false,
			BufferFlushInterval: 1 * time.Second,
			LocalAgentHostPort:  JaegerHostPort,
		},
	}
	tracer, closer, err := cfg.NewTracer()
	return tracer, closer, err
}

func SentryTracer(SentryDsn string) error {
	err := sentry.Init(sentry.ClientOptions{
		Dsn: SentryDsn,
	})
	return err
}
