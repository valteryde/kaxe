"""
Plot3D Render Pipeline Diagram Generator

This script creates a comprehensive flowchart diagram showing the rendering pipeline
used by the Plot3D class in Kaxe. The diagram illustrates the complete flow from
initialization to final image output, including all major decision points and
processing stages.

The render pipeline consists of several key phases:
1. Initialization and Setup
2. 3D Scene Construction  
3. Dynamic Axis Positioning
4. 2D Overlay Generation
5. Final Image Composition

Usage:
    python d3_render_pipeline_diagram.py
    
This will generate 'plot3d_render_pipeline.png' showing the complete flow.
"""

import graphviz

def create_plot3d_render_pipeline_diagram():
    """
    Create a detailed flowchart of the Plot3D rendering pipeline.
    
    Returns
    -------
    graphviz.Digraph
        The complete render pipeline diagram
    """
    
    # Create main flowchart
    dot = graphviz.Digraph(
        name='plot3d_render_pipeline',
        comment='Plot3D Rendering Pipeline',
        format='png'
    )
    
    # Set graph attributes for better layout
    dot.attr(rankdir='TB', size='12,16', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')

    # ===== COLOR SCHEME =====
    colors = {
        'start': '#E8F5E8',      # Light green
        'setup': '#E8F0FF',      # Light blue  
        'geometry': '#FFF0E8',   # Light orange
        'analysis': '#F0E8FF',   # Light purple
        'rendering': '#FFE8F0',  # Light pink
        'output': '#E8FFE8',     # Light green
        'decision': '#FFFFE0',   # Light yellow
        'critical': '#FFE8E8'    # Light red
    }

    # ===== INITIALIZATION PHASE =====
    with dot.subgraph(name='cluster_init') as init:
        init.attr(label='Initialization Phase', style='dashed', color='blue')
        
        init.node('start', 'User calls\nshow() or save()', 
                 fillcolor=colors['start'], shape='ellipse')
        init.node('start_method', '__start__()\nSetup GUI environment', 
                 fillcolor=colors['setup'])
        init.node('get_attrs', 'Get rendering attributes\n(width, height, colors)', 
                 fillcolor=colors['setup'])
        init.node('before', '__before__()\nInitialize 3D environment', 
                 fillcolor=colors['setup'])

    # ===== 3D SETUP SUBGRAPH =====
    with dot.subgraph(name='cluster_3d_setup') as setup_3d:
        setup_3d.attr(label='3D Scene Setup (__before__ method)', style='dashed', color='orange')
        
        setup_3d.node('coord_system', 'Setup coordinate system\n• Normalize axis bounds\n• Calculate scaling factors', 
                     fillcolor=colors['geometry'])
        setup_3d.node('opengl_init', 'Initialize OpenGL Renderer\n• Set camera angles\n• Configure lighting\n• Set resolution', 
                     fillcolor=colors['geometry'])
        setup_3d.node('wireframe', '__createWireframe__()\nGenerate 8 vertices, 12 edges', 
                     fillcolor=colors['geometry'])
        setup_3d.node('scale_render', '__scaleRender__()\nFit geometry to viewport', 
                     fillcolor=colors['geometry'])
        setup_3d.node('style_wireframe', 'Apply wireframe styling\n• Set line colors\n• Configure visibility', 
                     fillcolor=colors['geometry'])

    # ===== RENDER LOOP =====
    with dot.subgraph(name='cluster_render_loop') as render_loop:
        render_loop.attr(label='Main Render Loop (overlay function)', style='dashed', color='red')
        
        render_loop.node('overlay_start', 'overlay() function called\n(for each frame/rotation)', 
                        fillcolor=colors['critical'], shape='ellipse')
        render_loop.node('update_camera', 'Update camera rotation\nrender.camera.satelite()', 
                        fillcolor=colors['analysis'])
        render_loop.node('after', '__after__()\nCore rendering logic', 
                        fillcolor=colors['critical'])

    # ===== AXIS POSITIONING ALGORITHM =====
    with dot.subgraph(name='cluster_axis') as axis:
        axis.attr(label='Dynamic Axis Positioning (__after__ method)', style='dashed', color='purple')
        
        axis.node('perf_check', 'Performance check\nSkip if rendering too fast?', 
                 fillcolor=colors['decision'], shape='diamond')
        axis.node('cleanup', 'Cleanup previous frame\n• Remove background triangles\n• Remove grid lines', 
                 fillcolor=colors['analysis'])
        axis.node('face_projection', 'Project cube faces to 2D\nCalculate screen coordinates', 
                 fillcolor=colors['analysis'])
        axis.node('face_culling', 'Face visibility detection\n• Calculate face normals\n• Check camera direction', 
                 fillcolor=colors['analysis'])
        axis.node('background', 'Draw background faces\n(if enabled)', 
                 fillcolor=colors['rendering'])
        axis.node('axis_selection', 'Optimal axis positioning\n• Test 12 edge candidates\n• Find closest to camera\n• Avoid face overlaps', 
                 fillcolor=colors['analysis'])
        axis.node('overlap_check', 'Axis overlap resolution\nUse alternative positions', 
                 fillcolor=colors['analysis'])
        axis.node('create_axes', 'Create axis objects\n• Generate tick marks\n• Add labels\n• Position arrows', 
                 fillcolor=colors['rendering'])
        axis.node('grid_lines', 'Generate grid lines\n(if background enabled)', 
                 fillcolor=colors['rendering'])

    # ===== 2D COMPOSITION =====
    with dot.subgraph(name='cluster_2d') as comp_2d:
        comp_2d.attr(label='2D Overlay Composition', style='dashed', color='green')
        
        comp_2d.node('include_all', '__includeAllAgain__()\nPosition all 2D elements', 
                    fillcolor=colors['rendering'])
        comp_2d.node('pillow_paint', '__pillowPaint__()\nRender 2D overlay to image', 
                    fillcolor=colors['rendering'])
        comp_2d.node('crop_overlay', 'Crop overlay to render size', 
                    fillcolor=colors['rendering'])

    # ===== FINAL OUTPUT =====
    with dot.subgraph(name='cluster_output') as output:
        output.attr(label='Final Image Generation', style='dashed', color='darkgreen')
        
        output.node('render_3d', 'render.render(overlay)\nCompose 3D + 2D layers', 
                   fillcolor=colors['output'])
        output.node('final_crop', 'Crop to content bounds\nApply padding', 
                   fillcolor=colors['output'])
        output.node('save_or_display', 'Output final image\n• Save to file\n• Display in GUI', 
                   fillcolor=colors['output'], shape='ellipse')

    # ===== DECISION NODES =====
    dot.node('gui_check', 'GUI mode?', fillcolor=colors['decision'], shape='diamond')
    dot.node('cache_check', 'Use cached\naxis positions?', fillcolor=colors['decision'], shape='diamond')
    dot.node('boxed_check', 'Boxed plot\nstyle?', fillcolor=colors['decision'], shape='diamond')
    dot.node('background_check', 'Background\nenabled?', fillcolor=colors['decision'], shape='diamond')

    # ===== MAIN FLOW CONNECTIONS =====
    # Initialization flow
    dot.edge('start', 'start_method')
    dot.edge('start_method', 'get_attrs')
    dot.edge('get_attrs', 'before')
    
    # 3D Setup flow
    dot.edge('before', 'coord_system')
    dot.edge('coord_system', 'opengl_init')
    dot.edge('opengl_init', 'wireframe')
    dot.edge('wireframe', 'scale_render')
    dot.edge('scale_render', 'style_wireframe')
    
    # Render loop entry
    dot.edge('style_wireframe', 'overlay_start')
    dot.edge('overlay_start', 'update_camera')
    dot.edge('update_camera', 'after')
    
    # Core rendering logic
    dot.edge('after', 'perf_check')
    dot.edge('perf_check', 'cleanup', label='continue')
    dot.edge('perf_check', 'cache_check', label='skip update')
    dot.edge('cleanup', 'face_projection')
    dot.edge('face_projection', 'boxed_check')
    
    # Boxed plot branch
    dot.edge('boxed_check', 'face_culling', label='yes')
    dot.edge('face_culling', 'background_check')
    dot.edge('background_check', 'background', label='yes')
    dot.edge('background_check', 'axis_selection', label='no')
    dot.edge('background', 'axis_selection')
    dot.edge('axis_selection', 'overlap_check')
    dot.edge('overlap_check', 'create_axes')
    dot.edge('create_axes', 'grid_lines')
    
    # Cache flow
    dot.edge('cache_check', 'create_axes', label='yes')
    
    # Alternative plot styles
    dot.edge('boxed_check', 'create_axes', label='no\n(center/empty style)')
    
    # 2D Composition flow
    dot.edge('grid_lines', 'include_all')
    dot.edge('include_all', 'pillow_paint')
    dot.edge('pillow_paint', 'crop_overlay')
    
    # Final output
    dot.edge('crop_overlay', 'render_3d')
    dot.edge('render_3d', 'final_crop')
    dot.edge('final_crop', 'gui_check')
    dot.edge('gui_check', 'save_or_display', label='save mode')
    
    # GUI loop back
    dot.edge('gui_check', 'overlay_start', 
             label='GUI mode\n(interactive loop)', 
             style='dashed', color='red')

    # ===== PERFORMANCE ANNOTATIONS =====
    # Add timing information as edge labels
    dot.edge('face_culling', 'background', label='~0.3ms', style='dotted', color='gray')
    dot.edge('axis_selection', 'overlap_check', label='~0.3ms', style='dotted', color='gray') 
    dot.edge('overlap_check', 'create_axes', label='~0.2ms', style='dotted', color='gray')
    dot.edge('create_axes', 'grid_lines', label='~1ms', style='dotted', color='gray')
    dot.edge('include_all', 'pillow_paint', label='~0.2ms', style='dotted', color='gray')

    return dot


def main():
    """Generate and save the Plot3D render pipeline diagram."""
    
    print("Generating Plot3D render pipeline diagram...")
    
    # Create the diagram
    diagram = create_plot3d_render_pipeline_diagram()
    
    # Save the diagram
    output_file = 'plot3d_render_pipeline'
    diagram.render(output_file, cleanup=True)
    
    print(f"✅ Diagram saved as '{output_file}.png'")
    print("\nDiagram Legend:")
    print("🟢 Green: Initialization and final output")
    print("🔵 Blue: Setup and configuration")
    print("🟠 Orange: 3D geometry operations")
    print("🟣 Purple: Analysis and calculations")
    print("🔴 Pink: Rendering operations")
    print("🟡 Yellow: Decision points")
    print("🔴 Red: Critical performance paths")
    print("\n📊 The diagram shows the complete flow from user input to final image,")
    print("including performance-critical sections and optimization points.")


if __name__ == '__main__':
    main()