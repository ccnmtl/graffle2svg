#!/usr/bin/python
#Copyright (c) 2009, Tim Wintle
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    * Neither the name of the project nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""simple geometry functions"""
import math

def findcentre(pts):
    """Finds the centre of the points ( *not* Centre of Mass)"""
    xmax,ymax,xmin,ymin = pts[0] + pts[0]
    for x,y in pts:
        if xmax < x:
            xmax = x
        elif xmin > x:
            xmin = x
        if ymax < y:
            ymax = y
        elif ymin > y:
            ymin = y
    return 0.5*(xmax+xmin), 0.5*(ymax+ymin)


def h_flip_points(pts,centre=None):
    """Horizontal flip"""
    if centre is None:
        centre = findcentre(pts)
    xc,yc = centre
    outpts = []
    for (x,y) in pts:
        outpts.append([xc + (-1. * (x-xc)), y])
    return outpts
    
    
def v_flip_points(pts,centre=None):
    """Vertical flip"""
    if centre is None:
        centre = findcentre(pts)
    xc,yc = centre
    outpts = []
    for (x,y) in pts:
        outpts.append([x, yc + (-1 * (y-yc))])
    return outpts
    
def rotate_points(pts, angle=0, centre=None):
    if centre is None:
        centre = findcentre(pts)
    if round(angle % 360,7) == 0:
        return pts
    elif round(angle % 180,7) == 0:
        return h_flip_points (
                   v_flip_points(pts, centre),
                   centre)
    # in radians
    phi = (angle * math.pi * 2.) / 360.
    xc,yc = centre
    outpts = []
    cs = math.cos(phi)
    sn = math.sin(phi)
    # angle we're changing by
    for (x,y) in pts:
        # relative to centres
        relx,rely = x-xc, y-yc
        if (relx,rely) == (0.,0.):
            outpts.append(0.,0.)
            continue
        newx = xc + (cs*relx-sn*rely)
        newy = yc + (sn*relx+cs*rely)
        outpts.append( [newx,newy] )
    return outpts
