# NFT Collection Analysis Dashboard

An interactive dashboard built with Streamlit to analyze NFT collections using the OpenSea API v2. View key statistics, recent sales activity, and browse NFT assets with their traits.

## Features

- 📊 **Key Statistics**: View floor price, total volume, sales count, and owner count
- 📈 **Activity Tracking**: Monitor recent sales with prices and timestamps
- 🖼️ **Asset Browser**: Browse NFTs in a collection with images and traits
- 🔐 **Secure API Handling**: Proper API key management with error handling
- ⚡ **Caching**: Optimized data fetching with caching for better performance
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Getting Started

1. Obtain an OpenSea API key:
   - Visit the [OpenSea Developer Portal](https://docs.opensea.io/reference/api-overview)
   - Sign up for an account
   - Generate your API key

2. Run the dashboard:
   ```bash
   streamlit run nft_dashboard_fixed.py
   ```

3. Enter your OpenSea API key in the sidebar when prompted

4. Enter an NFT collection slug (e.g., `boredapeyachtclub`, `cryptopunks`) to analyze

## Usage

### Setting Your API Key

You can set your OpenSea API key in two ways:

1. **Through the UI**: Enter it in the sidebar text input
2. **Environment Variable**: Set `OPENSEA_API_KEY` in your environment

### Test Collections

Try these popular collection slugs:
- `boredapeyachtclub`
- `cryptopunks`
- `doodles-official`
- `azuki`
- `clone-x`

### Dashboard Tabs

1. **📊 Key Stats**: Displays floor price, total volume, sales count, and owner count
2. **📈 Activity**: Shows recent sales with prices and timestamps
3. **🖼️ Browse Assets**: Grid view of NFTs with images and expandable traits

## Error Handling

The dashboard handles various API errors gracefully:
- **401 Unauthorized**: Invalid API key
- **404 Not Found**: Collection doesn't exist
- **429 Rate Limited**: Too many requests (rate limiting)
- **Timeouts**: Network timeouts with retry mechanisms

## Dependencies

- [Streamlit](https://streamlit.io/) - For the web interface
- [Requests](https://docs.python-requests.org/en/latest/) - For API calls
- [Pandas](https://pandas.pydata.org/) - For data processing

## Security

- Never commit your API key to version control
- The app masks your API key in the UI
- Use environment variables for production deployments

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data provided by the [OpenSea API](https://docs.opensea.io/reference/api-overview)
- Images hosted on IPFS and displayed through ipfs.io gateway