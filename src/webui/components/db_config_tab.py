"""
Database Configuration Management Tab Component
Allows users to save, load, and delete configurations from the database
"""
import json
import gradio as gr
from typing import Optional, Dict, Any, List
from src.webui.webui_manager import WebuiManager
from src.auth.auth_manager import AuthManager


def create_db_config_tab(ui_manager: WebuiManager, auth_manager: AuthManager):
    """
    Creates a database configuration management tab.
    Allows saving/loading/deleting configurations to/from MySQL database.
    """
    tab_components = {}
    
    with gr.Group():
        gr.Markdown("### 💾 Save Current Configuration to Database")
        with gr.Row():
            config_name_input = gr.Textbox(
                label="Configuration Name",
                placeholder="Enter a name for this configuration (e.g., 'My Agent Setup')",
                scale=2
            )
            config_description = gr.Textbox(
                label="Description (Optional)",
                placeholder="Brief description of this configuration",
                scale=2
            )
        save_to_db_button = gr.Button("💾 Save to Database", variant="primary")
        save_status = gr.Markdown(visible=False)
    
    with gr.Group():
        gr.Markdown("### 📂 Load Configuration from Database")
        with gr.Row():
            config_dropdown = gr.Dropdown(
                label="Select Configuration",
                choices=[],
                interactive=True,
                scale=3
            )
            refresh_configs_button = gr.Button("🔄 Refresh", scale=1)
        
        config_info = gr.Markdown(visible=False)
        
        with gr.Row():
            load_from_db_button = gr.Button("📂 Load Selected", variant="primary")
            delete_config_button = gr.Button("🗑️ Delete Selected", variant="stop")
        
        load_status = gr.Markdown(visible=False)
    
    with gr.Group():
        gr.Markdown("### 📋 Your Saved Configurations")
        configs_table = gr.Dataframe(
            headers=["ID", "Name", "Description", "Created", "Last Updated"],
            datatype=["number", "str", "str", "str", "str"],
            col_count=(5, "fixed"),
            interactive=False,
            visible=True
        )
    
    # Store config IDs for reference
    config_ids_state = gr.State(value={})
    
    tab_components.update(dict(
        config_name_input=config_name_input,
        config_description=config_description,
        save_to_db_button=save_to_db_button,
        save_status=save_status,
        config_dropdown=config_dropdown,
        refresh_configs_button=refresh_configs_button,
        config_info=config_info,
        load_from_db_button=load_from_db_button,
        delete_config_button=delete_config_button,
        load_status=load_status,
        configs_table=configs_table,
    ))
    
    # Event Handlers
    def save_config_to_db(config_name: str, description: str, *component_values):
        """Save current UI configuration to database"""
        if not auth_manager.is_authenticated():
            return gr.update(visible=True, value="❌ Please login to save configurations")
        
        if not config_name or not config_name.strip():
            return gr.update(visible=True, value="❌ Please enter a configuration name")
        
        # Build configuration data from components
        components = ui_manager.get_components()
        config_data = {}
        
        for i, comp in enumerate(components):
            if not isinstance(comp, gr.Button) and not isinstance(comp, gr.File):
                interactive = str(getattr(comp, "interactive", True)).lower()
                if interactive != "false":
                    comp_id = ui_manager.get_id_by_component(comp)
                    if i < len(component_values):
                        config_data[comp_id] = component_values[i]
        
        # Save to database
        result = auth_manager.save_configuration(
            config_name.strip(),
            json.dumps(config_data, default=str),
            description or ""
        )
        
        if result["success"]:
            return gr.update(visible=True, value=f"✅ {result['message']}")
        else:
            return gr.update(visible=True, value=f"❌ {result['error']}")
    
    def refresh_config_list():
        """Refresh the list of saved configurations"""
        if not auth_manager.is_authenticated():
            return (
                gr.update(choices=[], value=None),
                {},
                gr.update(value=[], visible=True),
                gr.update(visible=True, value="❌ Please login to view configurations")
            )
        
        result = auth_manager.get_configurations()
        
        if not result["success"]:
            return (
                gr.update(choices=[], value=None),
                {},
                gr.update(value=[], visible=True),
                gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}")
            )
        
        configs = result.get("configurations", [])
        
        if not configs:
            return (
                gr.update(choices=[], value=None),
                {},
                gr.update(value=[], visible=True),
                gr.update(visible=True, value="ℹ️ No saved configurations found. Save your first configuration above!")
            )
        
        # Build dropdown choices and ID mapping
        choices = []
        id_mapping = {}
        table_data = []
        
        for config in configs:
            config_id = config.get("id")
            name = config.get("config_name", "Unnamed")
            desc = config.get("description", "")
            created = str(config.get("created_at", ""))[:19]  # Trim to datetime
            updated = str(config.get("updated_at", ""))[:19]
            
            choices.append(name)
            id_mapping[name] = config_id
            table_data.append([config_id, name, desc, created, updated])
        
        return (
            gr.update(choices=choices, value=choices[0] if choices else None),
            id_mapping,
            gr.update(value=table_data, visible=True),
            gr.update(visible=False)
        )
    
    def load_config_from_db(config_name: str, config_ids: dict):
        """Load a configuration from the database"""
        if not auth_manager.is_authenticated():
            return [gr.update(visible=True, value="❌ Please login to load configurations")]
        
        if not config_name:
            return [gr.update(visible=True, value="❌ Please select a configuration")]
        
        result = auth_manager.load_configuration(config_name)
        
        if not result["success"]:
            return [gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}")]
        
        config = result.get("configuration", {})
        config_data_str = config.get("config_data", "{}")
        
        try:
            config_data = json.loads(config_data_str)
        except json.JSONDecodeError:
            return [gr.update(visible=True, value="❌ Invalid configuration data")]
        
        # Apply configuration to components
        updates = []
        components = ui_manager.get_components()
        
        for comp in components:
            comp_id = ui_manager.get_id_by_component(comp)
            if comp_id in config_data:
                value = config_data[comp_id]
                if comp.__class__.__name__ == "Chatbot":
                    updates.append(gr.Chatbot(value=value, type="messages"))
                else:
                    updates.append(comp.__class__(value=value))
            else:
                updates.append(gr.update())  # No change
        
        # Add status message at the beginning
        status_msg = gr.update(visible=True, value=f"✅ Configuration '{config_name}' loaded successfully!")
        
        return [status_msg] + updates
    
    def delete_config_from_db(config_name: str, config_ids: dict):
        """Delete a configuration from the database"""
        if not auth_manager.is_authenticated():
            return (
                gr.update(visible=True, value="❌ Please login to delete configurations"),
                gr.update(),
                {},
                gr.update()
            )
        
        if not config_name:
            return (
                gr.update(visible=True, value="❌ Please select a configuration to delete"),
                gr.update(),
                config_ids,
                gr.update()
            )
        
        result = auth_manager.delete_configuration_by_name(config_name)
        
        if result["success"]:
            # Refresh the list after deletion
            refresh_result = refresh_config_list()
            return (
                gr.update(visible=True, value=f"✅ {result['message']}"),
                refresh_result[0],  # dropdown
                refresh_result[1],  # config_ids
                refresh_result[2]   # table
            )
        else:
            return (
                gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}"),
                gr.update(),
                config_ids,
                gr.update()
            )
    
    def show_config_info(config_name: str, config_ids: dict):
        """Show information about selected configuration"""
        if not config_name:
            return gr.update(visible=False)
        
        if not auth_manager.is_authenticated():
            return gr.update(visible=False)
        
        result = auth_manager.load_configuration(config_name)
        
        if result["success"]:
            config = result.get("configuration", {})
            desc = config.get("description", "No description")
            created = str(config.get("created_at", ""))[:19]
            updated = str(config.get("updated_at", ""))[:19]
            
            info_text = f"**Description:** {desc}\n\n**Created:** {created} | **Last Updated:** {updated}"
            return gr.update(visible=True, value=info_text)
        
        return gr.update(visible=False)
    
    # Connect event handlers
    all_components = ui_manager.get_components()
    
    save_to_db_button.click(
        fn=save_config_to_db,
        inputs=[config_name_input, config_description] + all_components,
        outputs=[save_status]
    )
    
    refresh_configs_button.click(
        fn=refresh_config_list,
        inputs=[],
        outputs=[config_dropdown, config_ids_state, configs_table, load_status]
    )
    
    # Load outputs: status + all components
    load_outputs = [load_status] + all_components
    
    load_from_db_button.click(
        fn=load_config_from_db,
        inputs=[config_dropdown, config_ids_state],
        outputs=load_outputs
    )
    
    delete_config_button.click(
        fn=delete_config_from_db,
        inputs=[config_dropdown, config_ids_state],
        outputs=[load_status, config_dropdown, config_ids_state, configs_table]
    )
    
    config_dropdown.change(
        fn=show_config_info,
        inputs=[config_dropdown, config_ids_state],
        outputs=[config_info]
    )
    
    # Auto-refresh on tab load (triggered by demo.load)
    return tab_components, refresh_config_list, config_dropdown, config_ids_state, configs_table, load_status
