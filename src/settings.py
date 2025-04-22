import os
import json

class Settings:
    def get_config_dir(self):
        # This method is assumed to exist as it's called in the load_theme method
        pass

    def logger(self):
        # This method is assumed to exist as it's called in the load_theme method
        pass

    def load_theme(self, theme_name):
        """加载指定主题的配置数据
        
        Args:
            theme_name (str): 主题名称
            
        Returns:
            dict: 主题配置数据，如果主题不存在则返回None
        """
        # 主题文件路径
        theme_file = os.path.join(self.get_config_dir(), "themes", f"{theme_name}.json")
        
        # 如果自定义主题不存在，尝试加载内置主题
        if not os.path.exists(theme_file):
            builtin_theme_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "resources", "themes", f"{theme_name}.json"
            )
            if os.path.exists(builtin_theme_file):
                theme_file = builtin_theme_file
            else:
                return None
                
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载主题 {theme_name} 失败: {e}")
            return None 