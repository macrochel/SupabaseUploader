from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from datetime import date

url = "supabaseURL"
key = "supabaseToken"
client_options = ClientOptions(postgrest_client_timeout=None)
supabase: Client = create_client(url, key, options=client_options)

print("1 - Order\n2 - Implementation")
v = input()
if v == '1':
    v = input("Введите дату в формате: 'yyyy m d': ")
    v = v.split(' ')
    data = supabase.table("1S_orders_all").delete().eq("date", date(v[0], v[1], v[2])).execute()
elif v == '2':
    v = input("Введите дату в формате: 'yyyy m d': ")
    v = v.split(' ')
    data = supabase.table("1S_implementations_all").delete().eq("date", date(v[0], v[1], v[2])).execute()