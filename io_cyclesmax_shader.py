# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Export for Cycles for Max shader (.shader)",
    "author": "Jeff Witthuhn",
    "version": (0, 2, 1),
    "blender": (2, 83, 0),
    "location": "File > Export > Cycles for Max Shader (.shader)",
    "description": "Export Cycles shaders in a format compatible with Cycles for Max",
    "category": "Import-Export",
}

from enum import Enum
from math import floor

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

class NodeType(Enum):
    INVALID = "invalid"
    INCOMPATIBLE = "incompatible"
    # Color
    BRIGHT_CONTRAST = "bright_contrast"
    GAMMA = "gamma"
    HSV = "hsv"
    INVERT = "invert"
    LIGHT_FALLOFF = "light_falloff"
    MIX_RGB = "mix_rgb"
    RGB_CURVES = "rgb_curves"
    # Converter
    BLACKBODY = "blackbody"
    CLAMP = "clamp"
    COLOR_RAMP = "color_ramp"
    COMBINE_HSV = "combine_hsv"
    COMBINE_RGB = "combine_rgb"
    COMBINE_XYZ = "combine_xyz"
    # Untested
    MATH = "math"
    RGB_TO_BW = "rgb_to_bw"
    SEPARATE_HSV = "separate_hsv"
    SEPARATE_RGB = "separate_rgb"
    SEPARATE_XYZ = "separate_xyz"
    VECTOR_MATH = "vector_math"
    WAVELENGTH = "wavelength"
    # Shader
    AMBIENT_OCCLUSION = "ambient_occlusion"
    PRINCIPLED_BSDF = "principled_bsdf"
    MIX_SHADER = "mix_shader"
    ADD_SHADER = "add_shader"
    DIFFUSE_BSDF = "diffuse_bsdf"
    GLOSSY_BSDF = "glossy_bsdf"
    TRANSPARENT_BSDF = "transparent_bsdf"
    REFRACTION_BSDF = "refraction_bsdf"
    GLASS_BSDF = "glass_bsdf"
    TRANSLUCENT_BSDF = "translucent_bsdf"
    ANISOTROPIC_BSDF = "anisotropic_bsdf"
    VELVET_BSDF = "velvet_bsdf"
    TOON_BSDF = "toon_bsdf"
    SUBSURFACE_SCATTER = "subsurface_scatter"
    EMISSION = "emission"
    HAIR_BSDF = "hair_bsdf"
    HOLDOUT = "holdout"
    VOL_ABSORB = "vol_absorb"
    VOL_SCATTER = "vol_scatter"
    # Texture
    MAX_TEX = "max_tex"
    BRICK_TEX = "brick_tex"
    CHECKER_TEX = "checker_tex"
    GRADIENT_TEX = "gradient_tex"
    MAGIC_TEX = "magic_tex"
    MUSGRAVE_TEX = "musgrave_tex"
    NOISE_TEX = "noise_tex"
    VORONOI_TEX = "voronoi_tex"
    WAVE_TEX = "wave_tex"
    # Input
    BEVEL = "bevel"
    LIGHT_PATH = "light_path"
    FRESNEL = "fresnel"
    LAYER_WEIGHT = "layer_weight"
    CAMERA_DATA = "camera_data"
    TANGENT = "tangent"
    TEX_COORD = "texture_coordinate"
    GEOMETRY = "geometry"
    OBJECT_INFO = "object_info"
    RGB = "rgb"
    VALUE = "value"
    WIREFRAME = "wireframe"
    # Vector
    BUMP = "bump"
    DISPLACEMENT = "displacement"
    NORMAL_MAP = "normal_map"
    VECTOR_TRANSFORM = "vector_transform"
    # Output
    MATERIAL_OUTPUT = "out_material"

def get_type_by_idname_dict():
    output = dict()
    # Color
    output["ShaderNodeBrightContrast"] = NodeType.BRIGHT_CONTRAST
    output["ShaderNodeGamma"] = NodeType.GAMMA
    output["ShaderNodeHueSaturation"] = NodeType.HSV
    output["ShaderNodeInvert"] = NodeType.INVERT
    output["ShaderNodeLightFalloff"] = NodeType.LIGHT_FALLOFF
    output["ShaderNodeMixRGB"] = NodeType.MIX_RGB
    output["ShaderNodeRGBCurve"] = NodeType.RGB_CURVES
    # Converter
    output["ShaderNodeBlackbody"] = NodeType.BLACKBODY
    output["ShaderNodeClamp"] = NodeType.CLAMP
    output["ShaderNodeValToRGB"] = NodeType.COLOR_RAMP
    output["ShaderNodeCombineHSV"] = NodeType.COMBINE_HSV
    output["ShaderNodeCombineRGB"] = NodeType.COMBINE_RGB
    output["ShaderNodeCombineXYZ"] = NodeType.COMBINE_XYZ
    output["ShaderNodeMath"] = NodeType.MATH
    output["ShaderNodeRGBToBW"] = NodeType.RGB_TO_BW
    output["ShaderNodeSeparateHSV"] = NodeType.SEPARATE_HSV
    output["ShaderNodeSeparateRGB"] = NodeType.SEPARATE_RGB
    output["ShaderNodeSeparateXYZ"] = NodeType.SEPARATE_XYZ
    output["ShaderNodeVectorMath"] = NodeType.VECTOR_MATH
    output["ShaderNodeWavelength"] = NodeType.WAVELENGTH

    output["ShaderNodeAmbientOcclusion"] = NodeType.AMBIENT_OCCLUSION
    output["ShaderNodeBsdfPrincipled"] = NodeType.PRINCIPLED_BSDF
    output["ShaderNodeMixShader"] = NodeType.MIX_SHADER
    output["ShaderNodeAddShader"] = NodeType.ADD_SHADER
    output["ShaderNodeBsdfDiffuse"] = NodeType.DIFFUSE_BSDF
    output["ShaderNodeBsdfGlossy"] = NodeType.GLOSSY_BSDF
    output["ShaderNodeBsdfTransparent"] = NodeType.TRANSPARENT_BSDF
    output["ShaderNodeBsdfRefraction"] = NodeType.REFRACTION_BSDF
    output["ShaderNodeBsdfGlass"] = NodeType.GLASS_BSDF
    output["ShaderNodeBsdfTranslucent"] = NodeType.TRANSLUCENT_BSDF
    output["ShaderNodeBsdfAnisotropic"] = NodeType.ANISOTROPIC_BSDF
    output["ShaderNodeBsdfVelvet"] = NodeType.VELVET_BSDF
    output["ShaderNodeBsdfToon"] = NodeType.TOON_BSDF
    output["ShaderNodeSubsurfaceScattering"] = NodeType.SUBSURFACE_SCATTER
    output["ShaderNodeEmission"] = NodeType.EMISSION
    output["ShaderNodeBsdfHair"] = NodeType.HAIR_BSDF
    output["ShaderNodeHoldout"] = NodeType.HOLDOUT
    output["ShaderNodeVolumeAbsorption"] = NodeType.VOL_ABSORB
    output["ShaderNodeVolumeScatter"] = NodeType.VOL_SCATTER
    output["ShaderNodeTexBrick"] = NodeType.BRICK_TEX
    output["ShaderNodeTexChecker"] = NodeType.CHECKER_TEX
    output["ShaderNodeTexGradient"] = NodeType.GRADIENT_TEX
    output["ShaderNodeTexMagic"] = NodeType.MAGIC_TEX
    output["ShaderNodeTexMusgrave"] = NodeType.MUSGRAVE_TEX
    output["ShaderNodeTexNoise"] = NodeType.NOISE_TEX
    output["ShaderNodeTexVoronoi"] = NodeType.VORONOI_TEX
    output["ShaderNodeTexWave"] = NodeType.WAVE_TEX
    output["ShaderNodeBevel"] = NodeType.BEVEL
    output["ShaderNodeLightPath"] = NodeType.LIGHT_PATH
    output["ShaderNodeFresnel"] = NodeType.FRESNEL
    output["ShaderNodeLayerWeight"] = NodeType.LAYER_WEIGHT
    output["ShaderNodeCameraData"] = NodeType.CAMERA_DATA
    output["ShaderNodeTangent"] = NodeType.TANGENT
    output["ShaderNodeTexCoord"] = NodeType.TEX_COORD
    output["ShaderNodeNewGeometry"] = NodeType.GEOMETRY
    output["ShaderNodeObjectInfo"] = NodeType.OBJECT_INFO
    output["ShaderNodeRGB"] = NodeType.RGB
    output["ShaderNodeValue"] = NodeType.VALUE
    output["ShaderNodeWireframe"] = NodeType.WIREFRAME
    output["ShaderNodeBump"] = NodeType.BUMP
    output["ShaderNodeDisplacement"] = NodeType.DISPLACEMENT
    output["ShaderNodeNormalMap"] = NodeType.NORMAL_MAP
    output["ShaderNodeVectorTransform"] = NodeType.VECTOR_TRANSFORM
    output["ShaderNodeOutputMaterial"] = NodeType.MATERIAL_OUTPUT
    return output

class MaxTexManager:
    def __init__(self):
        self.slots_by_filename = dict()
        self.next_unassigned_slot = 1
    
    def get_empty_slot(self):
        return self.get_slot_from_filename("ThisIsABigUniqueStringThatIReallyHopeWontOverlapAnyRealFilePaths-IThinkMyOddsArePrettyGood")

    def get_slot_from_filename(self, filename):
        if filename in self.slots_by_filename:
            return self.slots_by_filename[filename]
        else:
            self.slots_by_filename[filename] = self.next_unassigned_slot
            self.next_unassigned_slot += 1
            return self.slots_by_filename[filename]

class CyclesNode:
    def __init__(self):
        self.float_values = dict()
        self.float3_values = dict()
        self.float4_values = dict()
        self.string_values = dict()
        self.int_values = dict()

    name = "unnamed"
    node_type = NodeType.INVALID
    position = (0.0, 0.0)

def add_node_strings(string_list, cycles_node):
    string_list.append(cycles_node.node_type.value)
    string_list.append(cycles_node.name)
    string_list.append(str(cycles_node.position[0]))
    string_list.append(str(cycles_node.position[1]))
    for name, value in cycles_node.float_values.items():
        string_list.append(name)
        string_list.append("{0:.4f}".format(value))
    for name, value in cycles_node.float3_values.items():
        string_list.append(name)
        string_list.append("{0:.4f},{1:.4f},{2:.4f}".format(value[0], value[1], value[2]))
    for name, value in cycles_node.float4_values.items():
        string_list.append(name)
        string_list.append("{0:.4f},{1:.4f},{2:.4f}".format(value[0], value[1], value[2]))
    for name, value in cycles_node.string_values.items():
        string_list.append(name)
        string_list.append(value)
    for name, value in cycles_node.int_values.items():
        string_list.append(name)
        string_list.append(str(value))
    string_list.append("node_end")

def get_single_curve_string(curve):
    output_list = list()
    for this_point in curve.points:
        location = this_point.location
        if (location[0] < 0 or location[1] < 0 or location[0] > 1 or location[1] > 1):
            continue
        output_list.append(str(location[0]))
        output_list.append(str(location[1]))
        if this_point.handle_type == 'VECTOR':
            output_list.append('l')
        else:
            output_list.append('h')
    return ",".join(output_list)

def get_rgb_curve_string(r_curve, g_curve, b_curve, c_curve):
    output_list = list()
    output_list.append("curve_rgb_00")
    output_list.append("00")
    output_list.append(get_single_curve_string(c_curve))
    output_list.append(get_single_curve_string(r_curve))
    output_list.append(get_single_curve_string(g_curve))
    output_list.append(get_single_curve_string(b_curve))
    return "/".join(output_list)

def get_ramp_string(ramp):
    output_list = list()
    output_list.append("ramp00")
    for this_element in ramp.elements:
        output_list.append(str(this_element.position))
        output_list.append(str(this_element.color[0]))
        output_list.append(str(this_element.color[1]))
        output_list.append(str(this_element.color[2]))
        output_list.append(str(this_element.alpha))
    return ",".join(output_list)

def get_cycles_node(type_by_idname, name, node, max_tex_manager):
    output = CyclesNode()
    location = node.location
    output.position = (floor(location[0]), -1.0 * floor(location[1]))
    output.name = name
    if node.bl_idname in type_by_idname:
        output.node_type = type_by_idname[node.bl_idname]
    elif node.bl_idname == "ShaderNodeTexImage":
        # Special case here because we convert image textures to max textures
        output.node_type = NodeType.MAX_TEX
        if node.image is None or node.image.filepath is None:
            output.int_values['slot'] = max_tex_manager.get_empty_slot()
        else:
            output.int_values['slot'] = max_tex_manager.get_slot_from_filename(node.image.filepath)
        return output
    else:
        output.node_type = NodeType.INVALID
        return output

    # Determine which sockets to copy based on node type
    copy_sockets = dict()
    # Color
    if output.node_type == NodeType.BRIGHT_CONTRAST:
        copy_sockets["Color"] = "color"
        copy_sockets["Bright"] = "bright"
        copy_sockets["Contrast"] = "contrast"
    elif output.node_type == NodeType.GAMMA:
        copy_sockets["Color"] = "color"
        copy_sockets["Gamma"] = "gamma"
    elif output.node_type == NodeType.HSV:
        copy_sockets["Hue"] = "hue"
        copy_sockets["Saturation"] = "saturation"
        copy_sockets["Value"] = "value"
        copy_sockets["Fac"] = "fac"
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.INVERT:
        copy_sockets["Fac"] = "fac"
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.LIGHT_FALLOFF:
        copy_sockets["Strength"] = "strength"
        copy_sockets["Smooth"] = "smooth"
    elif output.node_type == NodeType.MIX_RGB:
        copy_sockets["Fac"] = "fac"
        copy_sockets["Color1"] = "color1"
        copy_sockets["Color2"] = "color2"
    elif output.node_type == NodeType.RGB_CURVES:
        copy_sockets["Fac"] = "fac"
        copy_sockets["Color"] = "color"
    # Converter
    elif output.node_type == NodeType.BLACKBODY:
        copy_sockets["Temperature"] = "temperature"
    elif output.node_type == NodeType.CLAMP:
        copy_sockets["Value"] = "value"
        copy_sockets["Min"] = "min"
        copy_sockets["Max"] = "max"
    elif output.node_type == NodeType.COLOR_RAMP:
        copy_sockets["Fac"] = "fac"
    elif output.node_type == NodeType.COMBINE_HSV:
        copy_sockets["H"] = "h"
        copy_sockets["S"] = "s"
        copy_sockets["V"] = "v"
    elif output.node_type == NodeType.COMBINE_RGB:
        copy_sockets["R"] = "r"
        copy_sockets["G"] = "g"
        copy_sockets["B"] = "b"
    elif output.node_type == NodeType.COMBINE_XYZ:
        copy_sockets["X"] = "x"
        copy_sockets["Y"] = "y"
        copy_sockets["Z"] = "z"
    elif output.node_type == NodeType.MATH:
        copy_sockets["Value"] = "value1"
        copy_sockets["Value_001"] = "value2"
        copy_sockets["Value.001"] = "value2"
        copy_sockets["Value_002"] = "value3"
        copy_sockets["Value.002"] = "value3"
    elif output.node_type == NodeType.RGB_TO_BW:
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.SEPARATE_HSV:
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.SEPARATE_RGB:
        copy_sockets["Image"] = "image"
    elif output.node_type == NodeType.SEPARATE_XYZ:
        copy_sockets["Vector"] = "vector"
    elif output.node_type == NodeType.VECTOR_MATH:
        copy_sockets["Vector"] = "vector1"
        copy_sockets["Vector_001"] = "vector2"
        copy_sockets["Vector.001"] = "vector2"
    elif output.node_type == NodeType.WAVELENGTH:
        copy_sockets["Wavelength"] = "wavelength"
    # Unsorted
    elif output.node_type == NodeType.AMBIENT_OCCLUSION:
        copy_sockets["Color"] = "color"
        copy_sockets["Distance"] = "distance"
    elif output.node_type == NodeType.MIX_SHADER:
        copy_sockets["Fac"] = "fac"
    elif output.node_type == NodeType.PRINCIPLED_BSDF:
        copy_sockets["Base Color"] = "base_color"
        copy_sockets["Subsurface"] = "subsurface"
        copy_sockets["Subsurface Radius"] = "subsurface_radius"
        copy_sockets["Subsurface Color"] = "subsurface_color"
        copy_sockets["Metallic"] = "metallic"
        copy_sockets["Specular"] = "specular"
        copy_sockets["Specular Tint"] = "specular_tint"
        copy_sockets["Roughness"] = "roughness"
        copy_sockets["Anisotropic"] = "anisotropic"
        copy_sockets["Anisotropic Rotation"] = "anisotropic_rotation"
        copy_sockets["Sheen"] = "sheen"
        copy_sockets["Sheen Tint"] = "sheen_tint"
        copy_sockets["Clearcoat"] = "clearcoat"
        copy_sockets["Clearcoat Roughness"] = "clearcoat_roughness"
        copy_sockets["IOR"] = "ior"
        copy_sockets["Transmission"] = "transmission"
    elif output.node_type == NodeType.DIFFUSE_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Roughness"] = "roughness"
    elif output.node_type == NodeType.GLOSSY_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Roughness"] = "roughness"
    elif output.node_type == NodeType.TRANSPARENT_BSDF:
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.REFRACTION_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Roughness"] = "roughness"
        copy_sockets["IOR"] = "IOR"
    elif output.node_type == NodeType.GLASS_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Roughness"] = "roughness"
        copy_sockets["IOR"] = "IOR"
    elif output.node_type == NodeType.TRANSLUCENT_BSDF:
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.ANISOTROPIC_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Roughness"] = "roughness"
        copy_sockets["Anisotropy"] = "anisotropy"
        copy_sockets["Rotation"] = "rotation"
    elif output.node_type == NodeType.VELVET_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Sigma"] = "sigma"
    elif output.node_type == NodeType.TOON_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Size"] = "size"
        copy_sockets["Smooth"] = "smooth"
    elif output.node_type == NodeType.SUBSURFACE_SCATTER:
        copy_sockets["Color"] = "color"
        copy_sockets["Scale"] = "scale"
        copy_sockets["Radius"] = "radius"
        copy_sockets["Texture Blur"] = "texture_blur"
    elif output.node_type == NodeType.EMISSION:
        copy_sockets["Color"] = "color"
        copy_sockets["Strength"] = "strength"
    elif output.node_type == NodeType.HAIR_BSDF:
        copy_sockets["Color"] = "color"
        copy_sockets["Offset"] = "offset"
        copy_sockets["RoughnessU"] = "roughness_U"
        copy_sockets["RoughnessV"] = "roughness_v"
    elif output.node_type == NodeType.VOL_ABSORB:
        copy_sockets["Color"] = "color"
        copy_sockets["Density"] = "density"
    elif output.node_type == NodeType.VOL_SCATTER:
        copy_sockets["Color"] = "color"
        copy_sockets["Density"] = "density"
        copy_sockets["Anisotropy"] = "anisotropy"
    elif output.node_type == NodeType.BRICK_TEX:
        copy_sockets["Color1"] = "color1"
        copy_sockets["Color2"] = "color2"
        copy_sockets["Mortar"] = "mortar"
        copy_sockets["Scale"] = "scale"
        copy_sockets["Mortar Size"] = "mortar_size"
        copy_sockets["Mortar Smooth"] = "mortar_smooth"
        copy_sockets["Bias"] = "bias"
        copy_sockets["Brick Width"] = "brick_width"
        copy_sockets["Row Height"] = "row_height"
    elif output.node_type == NodeType.CHECKER_TEX:
        copy_sockets["Color1"] = "color1"
        copy_sockets["Color2"] = "color2"
        copy_sockets["Scale"] = "scale"
    elif output.node_type == NodeType.MAGIC_TEX:
        copy_sockets["Scale"] = "scale"
        copy_sockets["Distortion"] = "distortion"
    elif output.node_type == NodeType.MUSGRAVE_TEX:
        copy_sockets["Scale"] = "scale"
        copy_sockets["Detail"] = "detail"
        copy_sockets["Dimension"] = "dimension"
        copy_sockets["Lacunarity"] = "lacunarity"
        copy_sockets["Offset"] = "offset"
        copy_sockets["Gain"] = "gain"
    elif output.node_type == NodeType.NOISE_TEX:
        copy_sockets["Scale"] = "scale"
        copy_sockets["Detail"] = "detail"
        copy_sockets["Distortion"] = "distortion"
    elif output.node_type == NodeType.VORONOI_TEX:
        copy_sockets["Scale"] = "scale"
        copy_sockets["W"] = "w"
        copy_sockets["Smoothness"] = "smoothness"
        copy_sockets["Randomness"] = "randomness"
    elif output.node_type == NodeType.WAVE_TEX:
        copy_sockets["Scale"] = "scale"
        copy_sockets["Distortion"] = "distortion"
        copy_sockets["Detail"] = "detail"
        copy_sockets["Detail Scale"] = "detail_scale"
    elif output.node_type == NodeType.BEVEL:
        copy_sockets["Radius"] = "radius"
    elif output.node_type == NodeType.FRESNEL:
        copy_sockets["IOR"] = "IOR"
    elif output.node_type == NodeType.LAYER_WEIGHT:
        copy_sockets["Blend"] = "blend"
    elif output.node_type == NodeType.WIREFRAME:
        copy_sockets["Size"] = "size"
    elif output.node_type == NodeType.BUMP:
        copy_sockets["Strength"] = "strength"
        copy_sockets["Distance"] = "distance"
    elif output.node_type == NodeType.DISPLACEMENT:
        copy_sockets["Height"] = "height"
        copy_sockets["Midlevel"] = "midlevel"
        copy_sockets["Scale"] = "scale"
    elif output.node_type == NodeType.NORMAL_MAP:
        copy_sockets["Strength"] = "strength"
        copy_sockets["Color"] = "color"
    elif output.node_type == NodeType.VECTOR_TRANSFORM:
        copy_sockets["Vector"] = "vector"

    # Copy all sockets with identifiers in copy_sockets
    for input_socket in node.inputs:
        if input_socket.identifier not in copy_sockets:
            continue
        if input_socket.type == "VALUE":
            output.float_values[copy_sockets[input_socket.identifier]] = input_socket.default_value
        elif input_socket.type == "RGBA":
            value = input_socket.default_value
            output.float4_values[copy_sockets[input_socket.identifier]] = (value[0], value[1], value[2], value[3])
        elif input_socket.type == "VECTOR":
            value = input_socket.default_value
            output.float3_values[copy_sockets[input_socket.identifier]] = (value[0], value[1], value[2])
        else:
            pass

    # Copy any non-standard node inputs like enums, bools and strings
    # Color
    if isinstance(node, bpy.types.ShaderNodeMixRGB):
        output.string_values['type'] = str(node.blend_type).lower()
        if node.use_clamp:
            output.int_values['use_clamp'] = 1
        else:
            output.int_values['use_clamp'] = 0
    elif isinstance(node, bpy.types.ShaderNodeRGBCurve):
        if len(node.mapping.curves) == 4:
            curve_r = node.mapping.curves[0]
            curve_g = node.mapping.curves[1]
            curve_b = node.mapping.curves[2]
            curve_c = node.mapping.curves[3]
            output.string_values['curves'] = get_rgb_curve_string(curve_r, curve_g, curve_b, curve_c)
        else:
            # Ignore curves if there aren't exactly 4
            pass
    # Converter
    elif isinstance(node, bpy.types.ShaderNodeClamp):
        output.string_values['type'] = str(node.clamp_type).lower()
    elif isinstance(node, bpy.types.ShaderNodeMath):
        output.string_values['type'] = str(node.operation).lower()
        if node.use_clamp:
            output.int_values['use_clamp'] = 1
        else:
            output.int_values['use_clamp'] = 0
    elif isinstance(node, bpy.types.ShaderNodeVectorMath):
        output.string_values['type'] = str(node.operation).lower()
    # Unsorted
    elif isinstance(node, bpy.types.ShaderNodeAmbientOcclusion):
        output.int_values["samples"] = node.samples
        if node.inside:
            output.int_values["inside"] = 1
        else:
            output.int_values["inside"] = 0
        if node.only_local:
            output.int_values["only_local"] = 1
        else:
            output.int_values["only_local"] = 0
    elif isinstance(node, bpy.types.ShaderNodeBsdfGlossy):
        if node.distribution == 'MULTI_GGX':
            output.string_values['distribution'] = 'multiscatter_ggx'
        else:
            output.string_values['distribution'] = str(node.distribution).lower()
    elif isinstance(node, bpy.types.ShaderNodeBsdfRefraction):
        output.string_values['distribution'] = str(node.distribution).lower()
    elif isinstance(node, bpy.types.ShaderNodeBsdfGlass):
        if node.distribution == 'MULTI_GGX':
            output.string_values['distribution'] = 'multiscatter_ggx'
        else:
            output.string_values['distribution'] = str(node.distribution).lower()
    elif isinstance(node, bpy.types.ShaderNodeBsdfAnisotropic):
        if node.distribution == 'MULTI_GGX':
            output.string_values['distribution'] = 'multiscatter_ggx'
        else:
            output.string_values['distribution'] = str(node.distribution).lower()
    elif isinstance(node, bpy.types.ShaderNodeBsdfToon):
        output.string_values['component'] = str(node.component).lower()
    elif isinstance(node, bpy.types.ShaderNodeSubsurfaceScattering):
        output.string_values['falloff'] = str(node.falloff).lower()
    elif isinstance(node, bpy.types.ShaderNodeBsdfHair):
        output.string_values['component'] = str(node.component).lower()
    elif isinstance(node, bpy.types.ShaderNodeTexBrick):
        output.float_values['offset'] = node.offset
        output.int_values['offset_frequency'] = node.offset_frequency
        output.float_values['squash'] = node.squash
        output.int_values['squash_frequency'] = node.squash_frequency 
    elif isinstance(node, bpy.types.ShaderNodeTexGradient):
        output.string_values['type'] = str(node.gradient_type).lower()
    elif isinstance(node, bpy.types.ShaderNodeTexMagic):
        output.int_values['depth'] = node.turbulence_depth 
    elif isinstance(node, bpy.types.ShaderNodeTexMusgrave):
        if node.musgrave_type == "FBM":
            output.string_values['type'] = "fBM"
        else:
            output.string_values['type'] = str(node.musgrave_type).lower()
    elif isinstance(node, bpy.types.ShaderNodeTexVoronoi):
        if node.voronoi_dimensions == '1D':
            output.int_values['dimensions'] = 1
        elif node.voronoi_dimensions == '2D':
            output.int_values['dimensions'] = 2
        elif node.voronoi_dimensions == '3D':
            output.int_values['dimensions'] = 3
        elif node.voronoi_dimensions == '4D':
            output.int_values['dimensions'] = 4
        output.string_values['metric'] = str(node.distance).lower()
        output.string_values['feature'] = str(node.feature).lower()
    elif isinstance(node, bpy.types.ShaderNodeTexWave):
        output.string_values['type'] = str(node.wave_type).lower()
        if node.wave_profile == "SIN":
            output.string_values['profile'] = "sine"
        else:
            output.string_values['profile'] = str(node.wave_profile).lower()
    elif isinstance(node, bpy.types.ShaderNodeBevel):
        output.int_values['samples'] = node.samples
    elif isinstance(node, bpy.types.ShaderNodeTangent):
        output.string_values['direction'] = str(node.direction_type).lower()
        output.string_values['axis'] = str(node.axis).lower()
    elif isinstance(node, bpy.types.ShaderNodeRGB):
        value = node.outputs[0].default_value
        output.float4_values['value'] = (value[0], value[1], value[2], value[3])
    elif isinstance(node, bpy.types.ShaderNodeValue):
        output.float_values['value'] = node.outputs[0].default_value
    elif isinstance(node, bpy.types.ShaderNodeWireframe):
        if node.use_pixel_size:
            output.int_values['use_pixel_size'] = 1
        else:
            output.int_values['use_pixel_size'] = 0
    elif isinstance(node, bpy.types.ShaderNodeDisplacement):
        output.string_values['space'] = str(node.space).lower()
    elif isinstance(node, bpy.types.ShaderNodeNormalMap):
        if node.space == 'BLENDER_OBJECT':
            output.string_values['space'] = 'object'
        elif node.space == 'BLENDER_WORLD':
            output.string_values['space'] = 'world'
        else:
            output.string_values['space'] = str(node.space).lower()
    elif isinstance(node, bpy.types.ShaderNodeValToRGB):
        output.string_values['ramp'] = get_ramp_string(node.color_ramp)
    elif isinstance(node, bpy.types.ShaderNodeVectorTransform):
        output.string_values['type'] = str(node.vector_type).lower()
        output.string_values['convert_from'] = str(node.convert_from).lower()
        output.string_values['convert_to'] = str(node.convert_to).lower()

    return output


class CyclesConnection:
    def __init__(self):
        self.source_node = ""
        self.source_socket = ""
        self.dest_node = ""
        self.dest_socket = ""

class GetConnectionResult:
    def __init__(self):
        self.is_valid = False
        self.connection = CyclesConnection()

def get_cycles_connection(names_by_bname, link):
    output = GetConnectionResult()
    source_node = link.from_node
    dest_node = link.to_node
    if source_node.name not in names_by_bname:
        return output
    if dest_node.name not in names_by_bname:
        return output
    output.is_valid = True
    output.connection.source_node = names_by_bname[source_node.name]
    output.connection.dest_node = names_by_bname[dest_node.name]
    output.connection.source_socket = link.from_socket.name
    output.connection.dest_socket = link.to_socket.name
    
    # Some node types do not have matching socket names in the Cycles C++ api and the Blender Python api
    # For these types, change to the C++ name
    if source_node.bl_idname == "ShaderNodeMixShader":
        if link.from_socket.identifier == "Shader":
            output.connection.source_socket = "Closure"
    elif source_node.bl_idname == "ShaderNodeAddShader":
        if link.from_socket.identifier == "Shader":
            output.connection.source_socket = "Closure"

    if dest_node.bl_idname == "ShaderNodeMixShader":
        if link.to_socket.identifier == "Shader":
            output.connection.dest_socket = "Closure1"
        elif link.to_socket.identifier == "Shader_001":
            output.connection.dest_socket = "Closure2"
        elif link.to_socket.identifier == "Shader.001":
            output.connection.dest_socket = "Closure2"
    elif dest_node.bl_idname == "ShaderNodeAddShader":
        if link.to_socket.identifier == "Shader":
            output.connection.dest_socket = "Closure1"
        elif link.to_socket.identifier == "Shader_001":
            output.connection.dest_socket = "Closure2"
        elif link.to_socket.identifier == "Shader.001":
            output.connection.dest_socket = "Closure2"
    elif dest_node.bl_idname == "ShaderNodeMath":
        if link.to_socket.identifier == "Value":
            output.connection.dest_socket = "Value1"
        elif link.to_socket.identifier == "Value_001":
            output.connection.dest_socket = "Value2"
        elif link.to_socket.identifier == "Value.001":
            output.connection.dest_socket = "Value2"
        elif link.to_socket.identifier == "Value_002":
            output.connection.dest_socket = "Value3"
        elif link.to_socket.identifier == "Value.002":
            output.connection.dest_socket = "Value3"
    elif dest_node.bl_idname == "ShaderNodeVectorMath":
        if link.to_socket.identifier == "Vector":
            output.connection.dest_socket = "Vector1"
        elif link.to_socket.identifier == "Vector_001":
            output.connection.dest_socket = "Vector2"
        elif link.to_socket.identifier == "Vector.001":
            output.connection.dest_socket = "Vector2"
    
    return output

class SerializedNodeGraph:
    def __init__(self):
        self.graph_string = ""
        self.unsupported_types = set()
        self.incompatible_types = set()

def serialize_node_graph(node_tree):
    output = SerializedNodeGraph()

    type_by_idname = get_type_by_idname_dict()
    node_names_by_bname = dict()
    nodes_by_name = dict()
    connections = list()

    max_tex_manager = MaxTexManager()

    next_node_index = 0
    for this_node in node_tree.nodes:
        next_node_index += 1
        internal_name = "node" + str(next_node_index)
        converted_node = get_cycles_node(type_by_idname, internal_name, this_node, max_tex_manager)
        if converted_node.node_type == NodeType.INCOMPATIBLE:
            output.incompatible_types.add(this_node.bl_idname)
        elif converted_node.node_type != NodeType.INVALID:
            node_names_by_bname[this_node.name] = internal_name
            nodes_by_name[internal_name] = converted_node
        else:
            output.unsupported_types.add(this_node.bl_idname)

    for this_link in node_tree.links:
        if this_link.is_valid:
            converted_link = get_cycles_connection(node_names_by_bname, this_link)
            if converted_link.is_valid:
                connections.append(converted_link.connection)


    output_list = list()

    output_list.append("cycles_shader")
    output_list.append("1")
    
    output_list.append("section_nodes")
    for cycles_node in nodes_by_name.values():
        add_node_strings(output_list, cycles_node)

    output_list.append("section_connections")
    for this_connection in connections:
        output_list.append(this_connection.source_node)
        output_list.append(this_connection.source_socket)
        output_list.append(this_connection.dest_node)
        output_list.append(this_connection.dest_socket)

    output.graph_string = ("|".join(output_list) + "|")
    return output

class ExportCyclesMaxShader(bpy.types.Operator, ExportHelper):
    """Cycles for Max Shader Exporter"""
    bl_idname = "export_shader.cyclesmax"
    bl_label = "Export Cycles for Max Shader"

    filename_ext = ".shader"
    filter_glob: StringProperty(
            default="*.shader",
            options={'HIDDEN'},
            )

    def execute(self, context):
        if context.scene.render.engine != 'CYCLES' and context.scene.render.engine != 'BLENDER_EEVEE':
            self.report({'ERROR'}, "Shader export is only compatible with Cycles or Eevee.")
            return {'FINISHED'}

        found_shader = False

        for this_object in context.selected_objects:
            if this_object.active_material is None:
                continue
            this_material = this_object.active_material
            if this_material.node_tree is None:
                continue
            this_node_tree = this_material.node_tree
            if len(this_node_tree.nodes) == 0:
                continue
            found_shader = True
            serialized_graph = serialize_node_graph(this_node_tree)
            if len(serialized_graph.unsupported_types) > 0:
                self.report({'WARNING'}, "Ignored unsupported node types: " + ", ".join(serialized_graph.unsupported_types))
            if len(serialized_graph.incompatible_types) > 0:
                self.report({'WARNING'}, "Ignored incompatible node types: " + ", ".join(serialized_graph.incompatible_types) + ". Load this .blend file in Blender 2.81 or newer to correct this.")
            output_file = open(self.filepath, "w")
            output_file.write(serialized_graph.graph_string)
            break

        if found_shader == False:
            self.report({'ERROR'}, "Failed to find shader on selected objects")

        return {'FINISHED'}

def menu_export(self, context):
    self.layout.operator(ExportCyclesMaxShader.bl_idname, text="Cycles for Max Shader (.shader)")

def register():
    bpy.utils.register_class(ExportCyclesMaxShader)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)
    bpy.utils.unregister_class(ExportCyclesMaxShader)

# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
