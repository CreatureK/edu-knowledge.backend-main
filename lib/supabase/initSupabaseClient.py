# 初始化Supabase
from langchain_community.vectorstores.supabase import SupabaseVectorStore
from supabase import create_client,Client
from supabase.lib.client_options import ClientOptions
import os
client_options = ClientOptions(postgrest_client_timeout=None)
url = os.environ.get('PYTHON_SUPABASE_URL')
key = os.environ.get('PYTHON_SUPABASE_ANNOKEY')
supabaseClient : Client = create_client(url, key,options=client_options)