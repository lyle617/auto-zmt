"""
Query S3 operation costs from data warehouse
"""

def get_s3_cost_query():
    """
    Generate SQL query to get S3 operation costs for specific buckets and paths
    
    Returns:
        str: SQL query string
    """
    return """
    SELECT 
        cur_time,
        bucket,
        path,
        pcpl_count AS write_count,
        other_count AS read_count,
        pcpl_count * 0.059 / 10000 AS write_cost,
        other_count * 0.0198 / 10000 AS read_cost
    FROM 
        dwd_govern_cost.s3_access_operation_cost
    WHERE 
        cur_time BETWEEN '20250110' AND '20250114'
        AND bucket = 'pupumall-dc-tmp'
        AND path IN (
            'bigdata/lingq/hudi_realtime_cow/orders_0106_bucket_cow',
            'bigdata/lingq/data_test/tmp/orders20250106121454'
        )
    ORDER BY 
        cur_time DESC;
    """

if __name__ == "__main__":
    print(get_s3_cost_query())