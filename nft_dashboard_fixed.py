import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import math

# Set page config
st.set_page_config(
    page_title="NFT Collection Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# API Configuration - SECURE YOUR API KEY
# IMPORTANT: Store your API key securely, never commit it to version control
# Initialize OPENSEA_API_KEY with a default placeholder.
# It will be overridden by sidebar input or environment variable if available.
OPENSEA_API_KEY = "YOUR_OPENSEA_API_KEY"
OPENSEA_API_BASE = "https://api.opensea.io/api/v2"

# You can also use an environment variable for more security:
import os
# OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY", OPENSEA_API_KEY) # Uncomment to use environment variable

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_collection_stats(slug, api_key):
    """
    Fetch collection statistics from OpenSea API v2
    
    Args:
        slug (str): NFT collection slug
        api_key (str): OpenSea API key
    
    Returns:
        dict: Collection statistics or None if error
    """
    if api_key == "YOUR_OPENSEA_API_KEY":
        st.error("⚠️ Please set your OpenSea API key. Check the sidebar for instructions.")
        return None
    
    # Debug print for API key (masked)
    # print(f"Using API Key (masked): {api_key[:4]}...{api_key[-4:]}")

    url = f"{OPENSEA_API_BASE}/collections/{slug}/stats"
    
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "NFT-Dashboard/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 401:
            st.error("🚫 Invalid API key. Please check your OpenSea API key.")
            return None
        elif response.status_code == 404:
            st.error(f"❌ Collection '{slug}' not found. Please check the slug.")
            return None
        elif response.status_code == 429:
            st.error("⏰ Rate limit exceeded. Please wait a moment and try again.")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        
        # Extract the main stats from the response
        if 'total' in data:
            return {
                'floor_price': float(data['total'].get('floor_price', 0)),
                'volume': float(data['total'].get('volume', 0)),
                'sales': int(data['total'].get('sales', 0)),
                'num_owners': int(data['total'].get('num_owners', 0))
            }
        else:
            st.warning("No statistics data available for this collection.")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🔥 API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"💥 Unexpected error: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_recent_sales(slug, api_key):
    """
    Fetch recent sales events for a collection
    
    Args:
        slug (str): NFT collection slug
        api_key (str): OpenSea API key
    
    Returns:
        pd.DataFrame: Recent sales data or None if error
    """
    if api_key == "YOUR_OPENSEA_API_KEY":
        return None
    
    url = f"{OPENSEA_API_BASE}/events/collection/{slug}"
    
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "NFT-Dashboard/1.0"
    }
    
    params = {
        "event_type": "sale",
        "limit": 20
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 401:
            return None
        elif response.status_code == 404:
            return None
        elif response.status_code == 429:
            st.warning("⏰ Rate limit exceeded for sales data.")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        
        if 'asset_events' in data and data['asset_events']:
            # Convert to DataFrame
            df = pd.DataFrame(data['asset_events'])
            
            # Extract relevant columns
            processed_data = []
            for _, event in df.iterrows():
                try:
                    # Convert price from Wei to ETH
                    total_price = float(event.get('total_price', 0)) / (10**18)
                    
                    # Get NFT name and ID
                    if 'asset' in event and event['asset']:
                        nft_name = event['asset'].get('name', 'Unknown')
                        nft_id = event['asset'].get('identifier', 'Unknown')
                    else:
                        nft_name = 'Unknown'
                        nft_id = 'Unknown'
                    
                    # Get payment token
                    payment_token = event.get('payment_token', {}).get('symbol', 'ETH')
                    
                    # Format timestamp
                    timestamp = event.get('event_timestamp', '')
                    if timestamp:
                        try:
                            formatted_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_time = timestamp
                    else:
                        formatted_time = 'Unknown'
                    
                    processed_data.append({
                        'NFT Name': nft_name,
                        'Token ID': nft_id,
                        'Price': f"{total_price:.4f} {payment_token}",
                        'Timestamp': formatted_time
                    })
                except Exception as e:
                    continue
            
            return pd.DataFrame(processed_data)
        else:
            return pd.DataFrame()
            
    except requests.exceptions.Timeout:
        st.warning("⏱️ Sales data request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"🔥 Failed to fetch recent sales: {str(e)}")
        return None
    except Exception as e:
        st.warning(f"💥 Error processing sales data: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_collection_assets(slug, api_key, limit=20):
    """
    Fetch NFT assets from a collection
    
    Args:
        slug (str): NFT collection slug
        api_key (str): OpenSea API key
        limit (int): Number of assets to fetch
    
    Returns:
        list: List of NFT assets or None if error
    """
    if api_key == "YOUR_OPENSEA_API_KEY":
        return None
    
    url = f"{OPENSEA_API_BASE}/assets/collection/{slug}"
    
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "NFT-Dashboard/1.0"
    }
    
    params = {
        "limit": limit,
        "order_by": "pk",
        "order_direction": "desc"
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            
            if response.status_code == 401:
                st.error("🚫 Invalid API key for assets. Please check your OpenSea API key.")
                return None
            elif response.status_code == 404:
                st.warning(f"❌ Collection '{slug}' not found for assets.")
                return []
            elif response.status_code == 429:
                st.warning(f"⏰ Rate limit exceeded for assets data. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt) # Exponential backoff
                continue # Retry
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'nfts' in data and data['nfts']:
                return data['nfts']
            else:
                return []
                
        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Assets data request timed out (attempt {attempt + 1}/{max_retries}). Retrying...")
            time.sleep(2 ** attempt) # Exponential backoff
            continue # Retry
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code >= 500:
                st.warning(f"🚨 Server error {e.response.status_code} (attempt {attempt + 1}/{max_retries}). Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt) # Exponential backoff
                continue # Retry
            else:
                st.error(f"🔥 Failed to fetch collection assets: {str(e)}")
                return None
        except Exception as e:
            st.error(f"💥 Error processing assets data: {str(e)}")
            return None
    
    st.error(f"❌ Failed to fetch assets after {max_retries} attempts due to timeout or rate limit.")
    return None

# Sidebar for API key configuration
with st.sidebar:
    st.header("🔑 API Configuration")
    
    # Option 1: Direct input (for testing only)
    api_key_input = st.text_input(
        "OpenSea API Key:",
        value="YOUR_OPENSEA_API_KEY",
        type="password",
        help="Enter your OpenSea API key. For production, use environment variables or Streamlit secrets."
    )
    
    if api_key_input != "YOUR_OPENSEA_API_KEY":
        OPENSEA_API_KEY = api_key_input
    
    st.markdown("### 🔗 Get Your API Key:")
    st.markdown("1. Go to [OpenSea Developer Portal](https://docs.opensea.io/reference/api-overview)")
    st.markdown("2. Sign up for an account")
    st.markdown("3. Generate your API key")
    st.markdown("4. Paste it above or set as environment variable")
    
    st.markdown("### 🧪 Test Collections:")
    st.markdown("- `boredapeyachtclub`")
    st.markdown("- `cryptopunks`")
    st.markdown("- `doodles-official`")
    st.markdown("- `azuki`")
    st.markdown("- `clone-x`")

# Main UI
st.title("NFT Collection Analysis Dashboard 📈")

# Collection slug input
collection_slug = st.text_input(
    "Enter NFT Collection Slug:", 
    value="boredapeyachtclub",
    help="Enter the collection slug (e.g., boredapeyachtclub, cryptopunks, doodles-official)"
)

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Key Stats", "📈 Activity", "🖼️ Browse Assets"])

# Fetch data when user provides a slug
if collection_slug and OPENSEA_API_KEY != "YOUR_OPENSEA_API_KEY":
    with st.spinner(f"Fetching data for '{collection_slug}'..."):
        stats = get_collection_stats(collection_slug, OPENSEA_API_KEY)
        recent_sales_df = get_recent_sales(collection_slug, OPENSEA_API_KEY)
        assets = get_collection_assets(collection_slug, OPENSEA_API_KEY)
    
    # Tab 1: Key Stats
    with tab1:
        st.header("Collection Statistics")
        
        if stats:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Floor Price",
                    value=f"{stats['floor_price']:.4f} ETH",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Total Volume",
                    value=f"{stats['volume']:.2f} ETH",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Total Sales",
                    value=f"{int(stats['sales']):,}",
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Total Owners",
                    value=f"{int(stats['num_owners']):,}",
                    delta=None
                )
            
            st.success(f"✅ Successfully loaded statistics for '{collection_slug}'")
        else:
            st.warning("No statistics available for this collection.")
    
    # Tab 2: Recent Activity
    with tab2:
        st.header("Recent Sales Activity")
        
        if recent_sales_df is not None and not recent_sales_df.empty:
            st.subheader("Recent Sales")
            st.dataframe(recent_sales_df, use_container_width=True)
            
            # Additional insights
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Recent Sales", len(recent_sales_df))
            with col2:
                # Extract numeric prices for average calculation
                prices = []
                for price_str in recent_sales_df['Price']:
                    try:
                        price = float(price_str.split()[0])
                        prices.append(price)
                    except:
                        continue
                
                if prices:
                    avg_price = sum(prices) / len(prices)
                    st.metric("Average Sale Price", f"{avg_price:.4f} ETH")
        else:
            st.warning("No recent sales data available for this collection.")
    
    # Tab 3: Browse Assets
    with tab3:
        st.header("Browse Collection Assets")
        
        if assets:
            st.subheader(f"Showing {len(assets)} NFTs from '{collection_slug}'")
            
            # Create grid layout
            cols_per_row = 4
            for i in range(0, len(assets), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(assets):
                        nft = assets[i + j]
                        with col:
                            # Display NFT image
                            image_url = nft.get('image_url', '')

                            if image_url:
                                # Cek apakah ini URL IPFS dan ubah ke HTTP Gateway
                                if image_url.startswith("ipfs://"):
                                    ipfs_hash = image_url.replace("ipfs://", "")
                                    image_url = f"https://ipfs.io/ipfs/{ipfs_hash}"

                                try:
                                    st.image(image_url, use_column_width=True)
                                except Exception as e:
                                    # Tampilkan URL yang gagal di-load untuk debugging
                                    st.info(f"🖼️ Image not available")
                                    st.caption(f"Failed URL: {image_url}")
                                    # st.caption(f"Error: {e}") # Uncomment untuk debug error
                            else:
                                st.info("🖼️ No image URL")
                            
                            # Display basic info
                            nft_name = nft.get('name', f"NFT #{nft.get('identifier', 'Unknown')}")
                            st.caption(f"**{nft_name}**")
                            st.caption(f"Token ID: {nft.get('identifier', 'Unknown')}")
                            
                            # Traits expander
                            with st.expander("View Traits"):
                                traits = nft.get('traits', [])
                                if traits:
                                    for trait in traits:
                                        trait_type = trait.get('trait_type', 'Unknown')
                                        trait_value = trait.get('value', 'Unknown')
                                        st.write(f"**{trait_type}:** {trait_value}")
                                else:
                                    st.write("No traits available")
        else:
            st.warning("No assets available for this collection.")

elif OPENSEA_API_KEY == "YOUR_OPENSEA_API_KEY":
    st.info("🔑 Please set your OpenSea API key in the sidebar to begin analysis.")
else:
    st.info("📝 Please enter a collection slug to begin analysis.")

# Add footer with instructions
with st.expander("📖 Instructions & Troubleshooting"):
    st.write("""
    ### How to use this dashboard:
    1. **Get an OpenSea API Key**: Sign up at [OpenSea Developer Portal](https://docs.opensea.io/reference/api-overview)
    2. **Set Your API Key**: Enter it in the sidebar or use environment variables
    3. **Enter Collection Slug**: Type the collection slug (e.g., 'boredapeyachtclub', 'cryptopunks')
    4. **Explore Tabs**:
       - **📊 Key Stats**: View main collection statistics
       - **📈 Activity**: Browse recent sales and activity
       - **🖼️ Browse Assets**: View NFTs in the collection with traits
    
    ### 🔧 Troubleshooting:
    - **401 Unauthorized**: Your API key is invalid or expired
    - **404 Not Found**: Collection slug doesn't exist
    - **429 Rate Limited**: Too many requests, wait and try again
    - **522 Server Error**: OpenSea server issue, try again later
    
    ### 🧪 Test Collections:
    - `boredapeyachtclub`
    - `cryptopunks`
    - `doodles-official`
    - `azuki`
    - `clone-x`
    """)

# Add last updated timestamp
st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")