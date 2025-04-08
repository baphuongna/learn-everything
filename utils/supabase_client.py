"""
Supabase client utility for interacting with Supabase API
"""
import os
from supabase import create_client, Client

class SupabaseClient:
    """
    Singleton class for interacting with Supabase
    """
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            # Initialize the Supabase client
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

            # Tạo Supabase client
            cls._client = create_client(supabase_url, supabase_key)
        return cls._instance

    @property
    def client(self) -> Client:
        """
        Get the Supabase client instance
        """
        return self._client

    def get_data(self, table_name, query_params=None):
        """
        Get data from a Supabase table with optional query parameters

        Args:
            table_name (str): The name of the table to query
            query_params (dict, optional): Query parameters for filtering, ordering, etc.

        Returns:
            dict: The query result
        """
        query = self._client.table(table_name).select("*")

        if query_params:
            if 'filter' in query_params:
                for filter_item in query_params['filter']:
                    column, operator, value = filter_item
                    query = query.filter(column, operator, value)

            if 'order' in query_params:
                for order_item in query_params['order']:
                    column, direction = order_item
                    query = query.order(column, desc=(direction.lower() == 'desc'))

            if 'limit' in query_params:
                query = query.limit(query_params['limit'])

            if 'offset' in query_params:
                query = query.offset(query_params['offset'])

        return query.execute()

    def insert_data(self, table_name, data):
        """
        Insert data into a Supabase table

        Args:
            table_name (str): The name of the table
            data (dict or list): The data to insert

        Returns:
            dict: The insert result
        """
        return self._client.table(table_name).insert(data).execute()

    def update_data(self, table_name, data, match_column, match_value):
        """
        Update data in a Supabase table

        Args:
            table_name (str): The name of the table
            data (dict): The data to update
            match_column (str): The column to match for the update
            match_value: The value to match

        Returns:
            dict: The update result
        """
        return self._client.table(table_name).update(data).eq(match_column, match_value).execute()

    def delete_data(self, table_name, match_column, match_value):
        """
        Delete data from a Supabase table

        Args:
            table_name (str): The name of the table
            match_column (str): The column to match for deletion
            match_value: The value to match

        Returns:
            dict: The delete result
        """
        return self._client.table(table_name).delete().eq(match_column, match_value).execute()

    def execute_rpc(self, function_name, params=None):
        """
        Execute a Postgres function (RPC) in Supabase

        Args:
            function_name (str): The name of the function to execute
            params (dict, optional): Parameters to pass to the function

        Returns:
            dict: The function result
        """
        if params:
            return self._client.rpc(function_name, params).execute()
        return self._client.rpc(function_name).execute()

# Create a singleton instance
supabase = SupabaseClient()
