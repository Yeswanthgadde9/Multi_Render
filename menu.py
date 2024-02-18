import nuke

menubar = nuke.menu("Nuke")
mymenu = menubar.addMenu("Yesh")
mymenu.addCommand("Multi Render", "import nuke_multi_render;nuke_multi_render.main()")