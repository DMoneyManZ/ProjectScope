// Destination-color blending only. No framebuffer readback or scene analysis.
import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
export const InvertEffect=GObject.registerClass(
class ProjectScopeInvertEffect extends Clutter.OffscreenEffect {
    vfunc_paint_target(node,context) {
        const pipeline=this.get_pipeline();
        if(pipeline && pipeline!==this._configuredPipeline) {
            pipeline.set_blend('RGB=ADD(SRC_COLOR*(1-DST_COLOR[RGB]),DST_COLOR*(1-SRC_COLOR[RGB])) A=ADD(SRC_COLOR,DST_COLOR*(1-SRC_COLOR[A]))');
            this._configuredPipeline=pipeline;
        }
        super.vfunc_paint_target(node,context);
    }
});
