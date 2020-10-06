import logging

from wrapt import wrap_function_wrapper
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import Span

logging_format = (
    '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
    '[trace_id=%(otel_trace_id)s span_id=%(otel_span_id)s] '
    '- %(message)s'
)


def padded_hex(num):
    return '{:016x}'.format(num)


def makeRecordPatched(makeRecord, instance, args, kwargs):
    rv = makeRecord(*args, **kwargs)
    span_id = ''
    trace_id = ''
    span = trace_api.get_current_span()
    if span is not None and isinstance(span, Span):
        ctx = span.get_context()
        span_id = padded_hex(ctx.span_id)
        trace_id = padded_hex(ctx.trace_id)
    setattr(rv, 'otel_trace_id', span_id)
    setattr(rv, 'otel_span_id', trace_id)
    return rv


def enable_trace_correlation(tracer=None):
  wrap_function_wrapper(logging, 'Logger.makeRecord', makeRecordPatched)
  logging.basicConfig(level=logging.INFO, format=logging_format)

