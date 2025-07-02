# server.py
import time
from collections import defaultdict
from threading import Thread, Lock
from flask import Flask, render_template
from flask_socketio import SocketIO
from scapy.all import sniff, IP, TCP, UDP, ICMP
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
traffic_stats = defaultdict(lambda: {'bytes': 0, 'packets': 0, 'location': None, 'pci_info': []})
stats_lock = Lock()
running = True

def get_ip_location(ip):
    """获取IP地理位置信息"""
    try:
        # 简单判断局域网地址
        if (ip.startswith('192.168.') or ip.startswith('10.') or 
            ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31):
            return {'country': 'LAN', 'city': 'Local Network', 'lat': 0, 'lon': 0}
        
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,lat,lon,query", timeout=2)
        data = response.json()
        if data.get('status') == 'success':
            return {
                'country': data.get('country', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0)
            }
    except Exception as e:
        print(f"IP location fetch error for {ip}: {e}")
    return {'country': 'Unknown', 'city': 'Unknown', 'lat': 0, 'lon': 0}

def get_pci_info(packet):
    """提取PCI信息"""
    pci = {}
    
    # 协议类型
    if TCP in packet:
        pci['protocol'] = 'TCP'
        pci['src_port'] = packet[TCP].sport
        pci['dst_port'] = packet[TCP].dport
        # 修复：将TCP标志位转换为字符串
        pci['flags'] = str(packet[TCP].flags)
    elif UDP in packet:
        pci['protocol'] = 'UDP'
        pci['src_port'] = packet[UDP].sport
        pci['dst_port'] = packet[UDP].dport
    elif ICMP in packet:
        pci['protocol'] = 'ICMP'
        pci['type'] = packet[ICMP].type
        pci['code'] = packet[ICMP].code
    else:
        pci['protocol'] = 'Other'
    
    return pci

def packet_handler(packet):
    """处理捕获的数据包"""
    global traffic_stats
    
    if IP in packet:
        src_ip = packet[IP].src
        length = len(packet)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # 获取PCI信息
        pci_info = get_pci_info(packet)
        
        with stats_lock:
            if traffic_stats[src_ip]['location'] is None:
                traffic_stats[src_ip]['location'] = get_ip_location(src_ip)
            traffic_stats[src_ip]['bytes'] += length
            traffic_stats[src_ip]['packets'] += 1
            
            # 添加PCI信息到列表（保留最近的5条）
            pci_entry = {
                'time': timestamp,
                'protocol': pci_info.get('protocol', 'N/A'),
                'src_port': pci_info.get('src_port', 'N/A'),
                'dst_port': pci_info.get('dst_port', 'N/A'),
                'flags': pci_info.get('flags', 'N/A'),
                'size': length
            }
            traffic_stats[src_ip]['pci_info'].append(pci_entry)
            
            # 只保留最近5条PCI记录
            if len(traffic_stats[src_ip]['pci_info']) > 5:
                traffic_stats[src_ip]['pci_info'] = traffic_stats[src_ip]['pci_info'][-5:]

def start_sniffing():
    """启动数据包捕获线程"""
    print("Starting packet capture...")
    sniff(prn=packet_handler, store=0, filter="ip")

def broadcast_stats():
    global running
    while running:
        time.sleep(2)
        with stats_lock:
            stats_to_send = []
            for ip, data in traffic_stats.items():
                location = data.get('location') or {}
                # 确保所有数据都是可序列化的
                pci_info = []
                for item in data.get('pci_info', []):
                    # 确保所有字段都是基本类型
                    pci_info.append({
                        'time': item['time'],
                        'protocol': item['protocol'],
                        'src_port': item['src_port'],
                        'dst_port': item['dst_port'],
                        'flags': item['flags'],  # 现在已经是字符串
                        'size': item['size']
                    })
                
                stats_to_send.append({
                    'ip': ip,
                    'bytes': data['bytes'],
                    'packets': data['packets'],
                    'country': location.get('country', 'Unknown'),
                    'city': location.get('city', 'Unknown'),
                    'lat': location.get('lat', 0),
                    'lon': location.get('lon', 0),
                    'pci_info': pci_info
                })
            socketio.emit('traffic_update', {'data': stats_to_send})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    sniff_thread = Thread(target=start_sniffing)
    sniff_thread.daemon = True
    sniff_thread.start()
    
    stats_thread = Thread(target=broadcast_stats)
    stats_thread.daemon = True
    stats_thread.start()
    
    print("Starting WebSocket server on http://localhost:5000")
    try:
        socketio.run(app, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        running = False
        print("\nShutting down...")