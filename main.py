import tensorflow as tf
import tensorflow.keras.layers as tf_layers
from tensorflow.keras import Input as tf_input
import os
import inspect 




def get_layer_dict(module):
    layer_dict = {}

    for name,obj in inspect.getmembers(module):
        # print(name)
        try:
            layer_args = {}
            arg_details = {}
            if isinstance(obj, type):
                    
                arg_spec = inspect.getfullargspec(obj.__init__)
                args = arg_spec.args[1:]
                defaults = arg_spec.defaults or []

                if defaults:
                    positional_args = args[:-len(defaults)]
                    keyword_args = args[-len(defaults):]
                
                else:
                    positional_args = args
                    keyword_args = []
                for i in positional_args:
                    layer_args["required"]=True
                    arg_details[i]=layer_args.copy()
                for i in range(len(keyword_args)):
                    layer_args["required"]=False
                    layer_args["default"]=defaults[i]
                    arg_details[keyword_args[i]]=layer_args.copy()

                layer_dict[name] = arg_details

        except :
            print(f"Error in {name}\n with positional args {positional_args} and keyword args {keyword_args} and defaults {defaults}")

    return layer_dict

def datatype_of(value):
    """
    This function takes a value and returns a string representation of its type and the value,
    formatted according to the given examples.
    """
    if isinstance(value, bool):  # Checking for Boolean first because Booleans are also Integers in Python
        return f"Bool.of({str(value).lower()})"
    elif isinstance(value, int):
        return f"Int.of({value})"
    elif isinstance(value, float):
        return f"Float.of({value})"
    elif isinstance(value, str):
        return f"Str.of(\"{value}\")"
    elif isinstance(value, tuple):
        # Recursively call datatype_of for each element in the tuple and format the output
        tuple_elements = ", ".join([datatype_of(elem) for elem in value])
        return f"Tuple.of({tuple_elements})"
    else:
        return f"None.of()"


def create_ts_files(layers, main_code=[]):
  

    for layer_name, params in layers.items():
        
        # Generate index.ts
        
        # Generate <layer_name>.config.ts
        config_lines = "["
        # line = ""
        for param_name, param_info in params.items():
            if config_lines!="[":
                config_lines += ","
            line = "{"
            line += f'name: "{param_name}"'
            if not param_info["required"]:
                # line["defaultValue"]= datatype_of(param_info["default"])
                line+=f', defaultValue: {datatype_of(param_info["default"])}'
            else:
                # line['isRequired']= str(param_info["required"]).lower()
                line+=f', isRequired: {str(param_info["required"]).lower()}'
            line += ' }'
            
            config_lines+=line+""
        
        config_lines += "]"
    

        if layer_name == "Input":
            code  = f"""{{name : "{layer_name}", nameTf : "{layer_name}", importLink : "from tensorflow.keras import Input" , args : """+config_lines+f"""}},\n"""
        else :
            code  = f"""{{name : "{layer_name}", nameTf : "{layer_name}", args : """+config_lines+f"""}},\n"""


        main_code+=code
    return main_code


def add_input(main_code, input_layer):
    input_details = {}
    layer_name = "Input"
    # try:
    arg_spec = inspect.getfullargspec(input_layer)
    args = arg_spec.args[1:]  # Exclude 'self'
    defaults = arg_spec.defaults or []
    
    if defaults:
        positional_args = args[:-len(defaults)]
        keyword_args = args[-len(defaults):]
    else:
        positional_args = args
        keyword_args = []
    arg_details = {}
    for arg in positional_args:
        arg_details[arg] = {"required": True}
    
    for i, arg in enumerate(keyword_args):
        arg_details[arg] = {"required": False, "default": defaults[i]}
    
    input_details[layer_name] = arg_details
    
    # Append the Input details to main_code
    
    code = create_ts_files(input_details, main_code)
    return code


if __name__ == "__main__":
    layer_dict = get_layer_dict(tf_layers)
    print("layer_dict ready")
    main_code = ''
    for layer, params in layer_dict.items():
        layer_inp = {layer: params}
        
        main_code = create_ts_files(layer_inp, main_code=main_code)
    
    # Add tf.keras.Input details
    main_code = add_input(main_code, tf_input)
    print("Processing finished")

    # Writing to file
    with open("all_layer.ts", "w+") as f:
        # Note: The format of main_code might need adjustments to correctly write into the file
        f.write("import { Bool, Float, Tuple,Int, None, Str } from \"@/packages/typewriter\";\n")
        f.write("import { LayerBaseConfig } from \"./types\";\n\n")
        f.write("export const LAYERS: LayerBaseConfig[] = [\n" + main_code+"\n]" )
    print("Writing finished")



