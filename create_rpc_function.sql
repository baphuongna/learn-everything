-- Tạo hàm RPC đơn giản để kiểm tra kết nối
CREATE OR REPLACE FUNCTION get_current_timestamp()
RETURNS TIMESTAMP WITH TIME ZONE
LANGUAGE SQL
AS $$
  SELECT NOW();
$$;

-- Cấp quyền cho anon và authenticated
GRANT EXECUTE ON FUNCTION get_current_timestamp() TO anon, authenticated;
