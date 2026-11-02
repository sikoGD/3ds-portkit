/* Original minimal homebrew demo: no game code, ROM, or game assets. */
#include <3ds.h>
#include <stdio.h>

int main(void) {
    gfxInitDefault();
    consoleInit(GFX_TOP, NULL);
    printf("3DS PortKit sample\n");
    printf("A minimal native homebrew starting point.\n\n");
    printf("Press START to quit.\n\n");
    u64 frames = 0;
    u64 start_ms = osGetTime();
    while (aptMainLoop()) {
        hidScanInput();
        if (hidKeysDown() & KEY_START) break;
        ++frames;
        if (!(frames % 30)) {
            u64 elapsed = osGetTime() - start_ms;
            printf("\x1b[6;0HFrames: %llu   ", (unsigned long long)frames);
            printf("\x1b[7;0HWall-clock FPS: %.2f   ", elapsed ? (frames * 1000.0 / elapsed) : 0.0);
        }
        gfxFlushBuffers();
        gfxSwapBuffers();
        gspWaitForVBlank();
    }
    gfxExit();
    return 0;
}
