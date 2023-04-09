from PIL import Image, ImageDraw, ImageFont, ImageColor
import pygame
import io

pygame.init()

WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h


def render_adjacent_img(pygame_display, img, spacing, adjacent_img_rect, alignment):
    img_rect = img.get_rect()

    print(adjacent_img_rect)
    if (alignment == "right"):
        # setattr(img_rect, "midleft",
        #         (adjacent_img_rect[0] + spacing, adjacent_img_rect[1]))
        position = (adjacent_img_rect.right + spacing, adjacent_img_rect.midright.y)
        
    elif (alignment == "bottom"):
        position = (adjacent_img_rect.x, adjacent_img_rect.top + spacing)
        # setattr(img_rect, "midtop",
        #         (adjacent_img_rect, adjacent_img_rect.bottom + spacing))

    pygame_display.blit(img, position)

    return img_rect


def render_adjacent_text(pygame_display, text, font, color, spacing, adjacent_img_rect, adjacency):
    img = font.render(text, True, color)
    img_rect = img.get_rect()

    if (adjacency == "right"):
        setattr(img_rect, "midleft",
                # (adjacent_img_rect.midright[0] + spacing, adjacent_img_rect.midright[1]))
                (adjacent_img_rect.right + spacing, adjacent_img_rect.midright[1]))
    elif (adjacency == "bottom"):
        setattr(img_rect, "topleft",
                (adjacent_img_rect.x, adjacent_img_rect.bottom + spacing))

    pygame_display.blit(img, img_rect)

    return img_rect


def render_img(pygame_display, img, offset, alignment):
    img_rect = img.get_rect()

    offset_x, offset_y = offset

    position = (0, 0)
    if (alignment == "topleft"):
        position = (0 + offset_x, 0 + offset_y)
    elif (alignment == "topright"):
        position = (WIDTH - offset_x, 0 + offset_y)
    elif (alignment == "bottomleft"):
        position = (0 + offset_x, HEIGHT - offset_y)
    elif (alignment == "bottomright"):
        position = (WIDTH - offset_x, HEIGHT - offset_y)
    elif (alignment == "midtop"):
        position = (WIDTH / 2, 0 + offset_y)

    setattr(img_rect, alignment, position)

    pygame_display.blit(img, img_rect)

    return img_rect


def render_text(pygame_display, font, text, color, offset, alignment, spacing):
    text_img = font.render(text, True, color)
    text_rect = text_img.get_rect()

    offset_x, offset_y = offset
    spacing_x, spacing_y = spacing

    position = (0, 0)
    if (alignment == "topleft"):
        position = (0 + offset_x, 0 + offset_y)
    elif (alignment == "topright"):
        position = (WIDTH - offset_x, 0 + offset_y)
    elif (alignment == "bottomleft"):
        position = (0 + offset_x, HEIGHT - offset_y)
    elif (alignment == "bottomright"):
        position = (WIDTH - offset_x, HEIGHT - offset_y)
    elif (alignment == "midtop"):
        position = (WIDTH / 2, 0 + offset_y)

    position = (position[0] + spacing_x, position[1] + spacing_y)

    setattr(text_rect, alignment, position)

    pygame_display.blit(text_img, text_rect)

    return text_rect


def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    # print position
    position = position[0], position[1]
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)
