#!/usr/bin/env python
# coding: utf-8

"""
When invoked on a Gimp image, this plugin will find a text layer and 
create animation frames from the text as if it's being typed out.

Thanks to Andreas Wilhelm for his sample here: 
http://avedo.net/487/typed-text-animation-with-python-gimp/
"""

from gimpfu import *

def message(msg):
	pdb.gimp_message(msg)

def text_type(gimp_image, gimp_drawable, wpm=60, ignore_spaces=True):

	# 1 word ~ 5 characters.
	ms_delay = 60000 / (wpm * 5)

	# Get the text layer:
	text_layer = None
	for layer in gimp_image.layers:
		if pdb.gimp_item_is_text_layer(layer):
			text_layer = layer
			break
	
	if not text_layer:
		raise Exception("Couldn't find a text layer in your image!")
		
	text = pdb.gimp_text_layer_get_text(text_layer)
	markup = pdb.gimp_text_layer_get_markup(text_layer)
	
	if markup and not text:
		# As far as I can tell, it got markup because I'd copied something
		# from a browser at one point?  :~(
		raise Exception("Your text layer has markup instead of text."
			+ " Try copying/pasting your text from a plain-text editor to fix it."
		)
	
	
	# Make a layer for each new character typed.
	next_layer_num = 1
	for x in xrange(len(text) + 1):
		sub_text = text[:x]
		if sub_text.endswith(" ") and ignore_spaces: continue
		layer_name = "Layer #{0} ({1} ms)".format(next_layer_num, ms_delay)
		next_layer_num += 1
	
		new_layer = pdb.gimp_layer_copy(text_layer, False) # Don't add alpha layer?
		# Put the layer on the top of our stack of layers:
		pdb.gimp_image_insert_layer(gimp_image, new_layer, None, 0)
		new_layer.name = layer_name
		pdb.gimp_text_layer_set_text(new_layer, sub_text)
		pdb.gimp_layer_set_visible(new_layer, True)
		
	# Assuming all went well, move the original layer to the top of the stack.
	# (It has all the text, so it should come last.)
	pdb.gimp_image_reorder_item(gimp_image, text_layer, None, 0)

def verbose_text_type(*args, **kwargs):
	"""Catch any exceptions and display them. """
	try:
		return atomic_text_type(*args, **kwargs)
	except Exception as e:
		msg = "Error in text_type: " + str(e)
		pdb.gimp_message(msg)

		
def atomic_text_type(*args, **kwargs):
	"""Group all of our work into a single undo."""
	gimp_image = args[0]
	try: 
		pdb.gimp_image_undo_group_start(gimp_image)
		return text_type(*args, **kwargs)
	finally:
		pdb.gimp_image_undo_group_end(gimp_image)
		
register(
	"text-type",
	 "Create typing animation frames from a text box already in your image.",
	 __doc__,
	 "Cody Casterline",
	 "Cody Casterline",
	 "2013",
	 "<Image>/Filters/Animation/Text _Type...",
	 "RGB*, GRAY*",
	 [
		(PF_INT, "wpm", "Words per minute", 60)
		, (PF_BOOL, "ignore_spaces", "Ignore Spaces", True)
	 ],
	 [], #(results)
	 verbose_text_type
)
main()
