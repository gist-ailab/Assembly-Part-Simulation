import argparse
from script.fileApi import get_logger

from assembly_manager import AssemblyManager

def get_args_parser():
    parser = argparse.ArgumentParser('Set IKEA Assembly Part Simulation', add_help=False)
    parser.add_argument('--furniture_name', default='STEFAN', type=str)
    parser.add_argument('--visualize', action='store_true')
    return parser

# test for joosoon branch

if __name__ == "__main__":
    """
        1. initialize part information from CAD files(*.STEP)
        2. Get Instruction Info and start assembly
        3. Create Assemlby Sequence
    """

    parser = argparse.ArgumentParser('Assembly Part Simulator', parents=[get_args_parser()])
    args = parser.parse_args()
    furniture_name = args.furniture_name
    is_visualize = args.visualize
    logger = get_logger(furniture_name)

    # Assembly manager    
    asm_manager = AssemblyManager(logger, furniture_name, is_visualize)

    # initialize part information from CAD
    asm_manager.initialize_CAD_info()
    
    
    # using part info to initialize scene
    asm_manager.initialize_part_to_scene()
    
    asm_manager.step()
    
    asm_manager.get_instruction_info()
    # assembly simulation
    while not asm_manager.is_end: # end sign from instruction_info
        # extract assembly info 
        asm_manager.compile_instruction_assembly_info()
        
        asm_manager.search_assembly_sequence()
        # assemble parts and calculate cost by distance taken during assembly
        asm_manager.simulate_instruction_assembly()

        asm_manager.simulate_hidden_assembly()
        
        asm_manager.compile_2_SNU_format()

        asm_manager.step()

        if is_visualize:
            asm_manager.visualization()

        asm_manager.get_instruction_info()
        
    #endregion
    if is_visualize:
        asm_manager.visualization()
    asm_manager.compile_whole_sequence(asm_manager.SNU_result_path)

        

