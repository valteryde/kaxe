import sys
import sdl2
import sdl2.ext
import sdl2.video
from OpenGL.GL import *


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

def init_opengl():
    glClearColor(0.1, 0.2, 0.3, 1.0)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

def render():
    glClear(GL_COLOR_BUFFER_BIT)

    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex2f(-0.5, -0.5)
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(0.5, -0.5)
    glColor3f(0.0, 0.0, 1.0)
    glVertex2f(0.0, 0.5)
    glEnd()

def main():
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        print("SDL_Init Error:", sdl2.SDL_GetError())
        return 1

    # OpenGL 2.1 context
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 1)

    window = sdl2.SDL_CreateWindow(b"PySDL2 + OpenGL Toggle Fullscreen",
                                   sdl2.SDL_WINDOWPOS_CENTERED,
                                   sdl2.SDL_WINDOWPOS_CENTERED,
                                   WINDOW_WIDTH, WINDOW_HEIGHT,
                                   sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_SHOWN)

    
    icon_surface = sdl2.ext.load_image("logo-small.png")
    sdl2.SDL_SetWindowIcon(window, icon_surface)

    if not window:
        print("SDL_CreateWindow Error:", sdl2.SDL_GetError())
        return 1

    gl_context = sdl2.SDL_GL_CreateContext(window)
    init_opengl()

    is_fullscreen = False
    running = True
    event = sdl2.SDL_Event()

    while running:
        while sdl2.SDL_PollEvent(event):
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif event.type == sdl2.SDL_KEYDOWN:
                # if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                #     running = False
                if event.key.keysym.sym == sdl2.SDLK_RETURN and (event.key.keysym.mod & sdl2.KMOD_ALT):
                    # Toggle fullscreen on Alt+Enter
                    if not is_fullscreen:
                        sdl2.SDL_SetWindowFullscreen(window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
                        is_fullscreen = True
                    else:
                        sdl2.SDL_SetWindowFullscreen(window, 0)
                        is_fullscreen = False
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                    width = event.window.data1
                    height = event.window.data2
                    glViewport(0, 0, width, height)

        render()
        sdl2.SDL_GL_SwapWindow(window)

    sdl2.SDL_GL_DeleteContext(gl_context)
    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
