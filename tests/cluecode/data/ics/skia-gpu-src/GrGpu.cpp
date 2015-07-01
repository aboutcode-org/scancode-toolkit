/*
    Copyright 2010 Google Inc.

    Licensed under the Apache License, Version 2.0 (the "License");

                GrPathRenderer* pr = NULL;
                const GrPath* clipPath = NULL;
                if (kRect_ClipType == clip.getElementType(c)) {
                    canRenderDirectToStencil = true;
                    fill = kEvenOdd_PathFill;
                } else {
                    fill = clip.getPathFill(c);
                    clipPath = &clip.getPath(c);
                    pr = this->getClipPathRenderer(*clipPath, NonInvertedFill(fill));
                    canRenderDirectToStencil =
                                                 NonInvertedFill(fill));
                }

                GrSetOp op = firstElement == c ? kReplace_SetOp : clip.getOp(c);
                int passes;
                GrStencilSettings stencilSettings[GrStencilSettings::kMaxStencilClipPasses];
                        0xffffffff,          0xffffffff,
                    };
                    SET_RANDOM_COLOR
                    if (kRect_ClipType == clip.getElementType(c)) {
                        this->setStencil(gDrawToStencil);
                        this->drawSimpleRect(clip.getRect(c), NULL, 0);
                    } else {
                        if (canRenderDirectToStencil) {
                for (int p = 0; p < passes; ++p) {
                    this->setStencil(stencilSettings[p]);
                    if (canDrawDirectToClip) {
                        if (kRect_ClipType == clip.getElementType(c)) {
                            SET_RANDOM_COLOR
                            this->drawSimpleRect(clip.getRect(c), NULL, 0);
                        } else {
                            SET_RANDOM_COLOR