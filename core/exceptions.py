class PipelineError(Exception):
    """Base exception for expected pipeline failures."""


class ExtractError(PipelineError):
    """Extraction or raw persistence failure."""


class TransformError(PipelineError):
    """Transformation or validation failure."""


class LoadError(PipelineError):
    """Destination persistence failure."""


class PipelineExecutionError(PipelineError):
    """Unexpected orchestration failure."""
