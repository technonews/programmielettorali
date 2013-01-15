# encoding: utf-8
'''
Created on 4 May 2012

@author: enrico
'''

from utils import load_table_data, get_headers, normalize_rows, normalize_cols

# please ignore the following for the time being
# TODO: the following is currently unused
style_string = """
<style type="text/css" >
    <![CDATA[
    
    circle.bubble {
        stroke: none;
        fill: blue;
    }
    
    ]]>
</style>
"""

def plot(filename):
    # load the data
    freq = load_table_data(filename)
    rows, cols = get_headers(freq)
    #normalize_rows(freq)
    #normalize_cols(freq)
    
    # take a subset of the data 
    # TODO: this should be done after sorting the arrays
    # but how to sort both of them?
    rows = rows[:100]
    cols = cols[:100]
    
    #print rows
    # calculate largest value to plot
    largest = max(freq.values())
    
    import svgfig as sf
    sf._canvas_defaults['viewBox'] = '0 0 5000 5000'
    sf._canvas_defaults['width'] = '5000px'
    sf._canvas_defaults['height'] = '5000px'
    
    # svg files are based a lot on 'groups'
    # groups are quite similar to illustrator groups
    # tranformations (scale, translate, rotate) can be applied
    # only on groups, NOT on items directly, so we often need 
    # to create a 'dumb' group with only one item in it..
    
    # here we create a group that contains everything else 
    # properties of groups are inherited by all items contained in them
    # if an item defines its own properties, this overrides the group properies 
    everything = sf.SVG("g", fill_opacity="100%")
    everything.attr['style'] = {
                                'stroke': 'none',
                                'fill': 'blue'
                                }
    
    # title of the graph
    # see http://www.w3schools.com/svg/svg_text.asp the SVG function
    # is shallow wrapper around svg
    title = sf.SVG("text", filename, font_size='13', x=20, y=35, fill="#333333", stroke="none", style="text-anchor:start; font-family:verdana;")
    line = sf.SVG("line", x1="20", y1="43", x2="620", y2="43", stroke="#000000", style="stroke-width: 1;")
    subtitle = sf.SVG("text", len(freq), font_size='12', x=20, y=60, fill="grey", stroke="none", style="text-anchor:start; font-family:verdana;")
    title_group = sf.SVG("g", title, subtitle, line)
    everything.append(title_group)
    
    # the size of the main body of the plot (bubbles) needs to be scaled
    # based on how many things we are plotting -- 
    # here we calculate the scale factor 
#    scale_factor =  340.0 / (len(cols) * 10.0)   
#    scale_string = 'scale(%f)' % (scale_factor)
#    bubbles_group = sf.SVG("g", 
#                           fill_opacity="100%",
#                           stroke="none",
#                           #width=len(cols)*10, height=len(rows)*10
#                           #transform=(translate_string + ' ' + scale_string)
#                           )

    bubbles_group = sf.SVG("g", fill_opacity="100%", stroke="none", transform='translate(120, 160), scale(2)')
    
    # draw a frame
    l = sf.SVG('rect', x=0, y=-5, width=len(cols)*10, height=len(rows)*10, fill='#dddddd', stroke="#ffffff", style="stroke-width: 1;")
    bubbles_group.append(l)
    
    # this for loop iterates over the column headers (cols) 
    # and plots each of them as a string, rotating each individually 
    for x, header in enumerate(cols):
        tx = 10 * (x + 1)
        ty = -8
        t = sf.SVG('text', header, x=tx, y=ty, fill='black', font_size='5', style="text-anchor:start; font-family:verdana;")
        tg = sf.SVG('g', t, transform='translate(-5,0)' 'rotate(%d, %d, %d)'%(-45, tx, ty))
        bubbles_group.append(tg)
        
        # draw vertical lines
        if x % 2 == 0 and len(rows) > 1:
            v = sf.SVG('rect', x=(10*x), y=-5, width=10, height=len(rows)*10, fill='none', stroke="#ffffff", style="stroke-width: 1;")
            bubbles_group.append(v)
    
    # this loop iterates over the actual data and plots it row by row
    # at the beginning of each row we also plot the row header
    for y, row_name in enumerate(rows):
        curr_y = 10*y
        t = sf.SVG('text', row_name, x=-5, y=curr_y+2, fill='black', font_size='5', style="text-anchor:end; font-family:verdana;")
        bubbles_group.append(t)
        
        # draw horizontal lines 
        if y % 2 == 0 and len(cols) > 1:
            h = sf.SVG('rect', x=0, y=curr_y-5, width=len(cols)*10, height=10, fill='none', stroke="#ffffff", style="stroke-width: 1;")
            bubbles_group.append(h)
                   
        # here we plot the actual data
        for x, col_name in enumerate(cols):
            val = freq[(row_name, col_name)]
            if [row_name] == [col_name]:
                r = sf.SVG("rect", x=10*x, y = curr_y-5, width=10, height=10, fill='#999999', stroke="#ffffff", style="stroke-width: 1;")
                bubbles_group.append(r)
            if val > 0 and [row_name] != [col_name]:
                val = float(val) * 2.0 / float(largest) * 2
                c = sf.SVG("circle", cx=10*x+5, cy=curr_y, r=val)
                c.attr['class'] = 'bubble'
                bubbles_group.append(c)
                
    everything.append(bubbles_group)
    
    # save to file
    # name the file according to input filename..
    out_filename = filename.replace('.txt', '.svg')
    out_filename = out_filename.replace('.csv', '.svg')
    print out_filename
    everything.save(out_filename)

if __name__ == '__main__':
    import sys, os
    filename = sys.argv[1]
    if os.path.isdir(filename):
        # this is a folder, look all csv files in it
        files = os.listdir(filename)
        files = filter(lambda x: x.endswith('.csv'), files)
        files = filter(lambda x: not 'net' in x, files)
        for f in files:
            try:
                plot(os.path.join(filename, f))
            except (ValueError, IndexError):
                continue
    else:
        plot(filename)