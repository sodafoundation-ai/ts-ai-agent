Available Tools:
execute_query(query: str, time: Optional[str] = None) -> Dict[str, Any]:
    """Execute an instant query against Prometheus.
    
    Args:
        query: PromQL query string
        time: Optional RFC3339 or Unix timestamp (default: current time)
        
    Returns:
        Query result with type (vector, matrix, scalar, string) and values
    """

execute_range_query(query: str, start: str, end: str, step: str) -> Dict[str, Any]:
    """Execute a range query against Prometheus.
    
    Args:
        query: PromQL query string
        start: Start time as RFC3339 or Unix timestamp
        end: End time as RFC3339 or Unix timestamp
        step: Query resolution step width (e.g., '15s', '1m', '1h')
        
    Returns:
        Range query result with type (usually matrix) and values over time
    """