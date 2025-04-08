"""
Script kiểm tra hiệu suất kết nối Supabase
"""
import os
import sys
import time
from pathlib import Path
import statistics

# Thêm thư mục gốc của dự án vào sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

def test_api_latency(iterations=10):
    """Kiểm tra độ trễ của Supabase API"""
    try:
        from utils.supabase_client import supabase
        
        print(f"Đang kiểm tra độ trễ API với {iterations} lần lặp...")
        latencies = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Thực hiện một truy vấn đơn giản
            supabase.client.table('_schema.tables').select('*').limit(1).execute()
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Chuyển đổi sang milliseconds
            latencies.append(latency)
            
            print(f"Lần {i+1}: {latency:.2f}ms")
            time.sleep(0.5)  # Tạm dừng giữa các lần gọi API
        
        # Tính toán thống kê
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        median_latency = statistics.median(latencies)
        
        print("\n=== KẾT QUẢ KIỂM TRA ĐỘ TRỄ API ===")
        print(f"Độ trễ trung bình: {avg_latency:.2f}ms")
        print(f"Độ trễ nhỏ nhất: {min_latency:.2f}ms")
        print(f"Độ trễ lớn nhất: {max_latency:.2f}ms")
        print(f"Độ trễ trung vị: {median_latency:.2f}ms")
        
        # Đánh giá
        if avg_latency < 200:
            print("Đánh giá: Rất tốt (< 200ms)")
        elif avg_latency < 500:
            print("Đánh giá: Tốt (200-500ms)")
        elif avg_latency < 1000:
            print("Đánh giá: Trung bình (500-1000ms)")
        else:
            print("Đánh giá: Chậm (> 1000ms)")
        
        return True
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra độ trễ API: {e}")
        return False

def test_database_latency(iterations=10):
    """Kiểm tra độ trễ của kết nối cơ sở dữ liệu"""
    try:
        import psycopg2
        
        # Lấy thông tin kết nối từ biến môi trường
        db_host = os.environ.get('SUPABASE_DB_HOST')
        db_port = os.environ.get('SUPABASE_DB_PORT')
        db_name = os.environ.get('SUPABASE_DB_NAME')
        db_user = os.environ.get('SUPABASE_DB_USER')
        db_password = os.environ.get('SUPABASE_DB_PASSWORD')
        
        if not all([db_host, db_port, db_name, db_user, db_password]):
            print("ERROR: Thiếu thông tin kết nối cơ sở dữ liệu")
            return False
        
        print(f"Đang kiểm tra độ trễ cơ sở dữ liệu với {iterations} lần lặp...")
        latencies = []
        
        # Kết nối đến PostgreSQL
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            sslmode='require'
        )
        
        for i in range(iterations):
            start_time = time.time()
            
            # Thực hiện một truy vấn đơn giản
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.fetchone()
            cursor.close()
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Chuyển đổi sang milliseconds
            latencies.append(latency)
            
            print(f"Lần {i+1}: {latency:.2f}ms")
            time.sleep(0.5)  # Tạm dừng giữa các lần truy vấn
        
        # Đóng kết nối
        conn.close()
        
        # Tính toán thống kê
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        median_latency = statistics.median(latencies)
        
        print("\n=== KẾT QUẢ KIỂM TRA ĐỘ TRỄ CƠ SỞ DỮ LIỆU ===")
        print(f"Độ trễ trung bình: {avg_latency:.2f}ms")
        print(f"Độ trễ nhỏ nhất: {min_latency:.2f}ms")
        print(f"Độ trễ lớn nhất: {max_latency:.2f}ms")
        print(f"Độ trễ trung vị: {median_latency:.2f}ms")
        
        # Đánh giá
        if avg_latency < 50:
            print("Đánh giá: Rất tốt (< 50ms)")
        elif avg_latency < 100:
            print("Đánh giá: Tốt (50-100ms)")
        elif avg_latency < 200:
            print("Đánh giá: Trung bình (100-200ms)")
        else:
            print("Đánh giá: Chậm (> 200ms)")
        
        return True
    except ImportError:
        print("ERROR: Không thể import psycopg2. Vui lòng cài đặt: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra độ trễ cơ sở dữ liệu: {e}")
        return False

def test_concurrent_connections(max_connections=10):
    """Kiểm tra khả năng xử lý kết nối đồng thời"""
    try:
        import concurrent.futures
        import psycopg2
        
        # Lấy thông tin kết nối từ biến môi trường
        db_host = os.environ.get('SUPABASE_DB_HOST')
        db_port = os.environ.get('SUPABASE_DB_PORT')
        db_name = os.environ.get('SUPABASE_DB_NAME')
        db_user = os.environ.get('SUPABASE_DB_USER')
        db_password = os.environ.get('SUPABASE_DB_PASSWORD')
        
        if not all([db_host, db_port, db_name, db_user, db_password]):
            print("ERROR: Thiếu thông tin kết nối cơ sở dữ liệu")
            return False
        
        def test_connection(i):
            try:
                # Kết nối đến PostgreSQL
                conn = psycopg2.connect(
                    host=db_host,
                    port=db_port,
                    dbname=db_name,
                    user=db_user,
                    password=db_password,
                    sslmode='require'
                )
                
                # Thực hiện một truy vấn đơn giản
                cursor = conn.cursor()
                cursor.execute("SELECT pg_sleep(0.5);")  # Giả lập truy vấn kéo dài
                cursor.fetchone()
                cursor.close()
                
                # Đóng kết nối
                conn.close()
                return True
            except Exception as e:
                return f"Lỗi kết nối {i}: {e}"
        
        print(f"Đang kiểm tra {max_connections} kết nối đồng thời...")
        start_time = time.time()
        
        # Sử dụng ThreadPoolExecutor để tạo nhiều kết nối đồng thời
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_connections) as executor:
            futures = [executor.submit(test_connection, i) for i in range(max_connections)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Đếm số kết nối thành công và thất bại
        success_count = sum(1 for result in results if result is True)
        failure_count = max_connections - success_count
        
        print("\n=== KẾT QUẢ KIỂM TRA KẾT NỐI ĐỒNG THỜI ===")
        print(f"Tổng số kết nối: {max_connections}")
        print(f"Kết nối thành công: {success_count}")
        print(f"Kết nối thất bại: {failure_count}")
        print(f"Thời gian hoàn thành: {total_time:.2f}s")
        
        # Hiển thị các lỗi nếu có
        if failure_count > 0:
            print("\nCác lỗi gặp phải:")
            for result in results:
                if result is not True:
                    print(f"- {result}")
        
        # Đánh giá
        success_rate = (success_count / max_connections) * 100
        if success_rate == 100:
            print(f"Đánh giá: Rất tốt (100% thành công)")
        elif success_rate >= 90:
            print(f"Đánh giá: Tốt ({success_rate:.1f}% thành công)")
        elif success_rate >= 70:
            print(f"Đánh giá: Trung bình ({success_rate:.1f}% thành công)")
        else:
            print(f"Đánh giá: Kém ({success_rate:.1f}% thành công)")
        
        return success_count > 0
    except ImportError as e:
        print(f"ERROR: Thiếu module cần thiết: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra kết nối đồng thời: {e}")
        return False

def run_performance_tests():
    """Chạy tất cả các kiểm tra hiệu suất"""
    print("=== KIỂM TRA HIỆU SUẤT KẾT NỐI SUPABASE ===")
    
    tests = [
        ("Kiểm tra độ trễ API", lambda: test_api_latency(5)),
        ("Kiểm tra độ trễ cơ sở dữ liệu", lambda: test_database_latency(5)),
        ("Kiểm tra kết nối đồng thời", lambda: test_concurrent_connections(5))
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"ERROR: Lỗi không xác định khi chạy kiểm tra: {e}")
            results.append(False)
    
    # Tổng kết
    print("\n=== KẾT QUẢ KIỂM TRA HIỆU SUẤT ===")
    for i, (name, _) in enumerate(tests):
        status = "PASS" if results[i] else "FAIL"
        print(f"{name}: {status}")
    
    # Đề xuất cải thiện
    print("\n=== ĐỀ XUẤT CẢI THIỆN HIỆU SUẤT ===")
    print("1. Sử dụng connection pooling để quản lý kết nối cơ sở dữ liệu")
    print("2. Tối ưu hóa truy vấn bằng cách sử dụng chỉ mục (index)")
    print("3. Sử dụng caching để giảm số lượng truy vấn")
    print("4. Sử dụng Supabase Functions cho các xử lý phức tạp")
    print("5. Giảm kích thước payload bằng cách chỉ chọn các trường cần thiết")
    print("6. Sử dụng Supabase Realtime cho các ứng dụng cần cập nhật theo thời gian thực")

if __name__ == "__main__":
    run_performance_tests()
