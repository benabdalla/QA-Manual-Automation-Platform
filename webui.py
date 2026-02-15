from dotenv import load_dotenv
load_dotenv()
import argparse
from src.webui.interface import theme_map, create_ui, create_ui_with_auth


def main():
    parser = argparse.ArgumentParser(description="Gradio WebUI for Browser Agent")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address to bind to")
    parser.add_argument("--port", type=int, default=7788, help="Port to listen on")
    parser.add_argument("--theme", type=str, default="Soft", choices=theme_map.keys(), help="Theme to use for the UI")
    parser.add_argument("--no-auth", action="store_true", help="Disable authentication (for development)")
    args = parser.parse_args()

    if args.no_auth:
        # Run without authentication
        demo = create_ui(theme_name=args.theme)
    else:
        # Run with authentication (requires XAMPP MySQL)
        demo = create_ui_with_auth(theme_name=args.theme)
    
    demo.queue().launch(server_name=args.ip, server_port=args.port)


if __name__ == '__main__':
    main()
