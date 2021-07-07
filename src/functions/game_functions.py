import sys
import pygame
from pygame.sprite import Group
from ..components.bullet import Bullet
from ..components.tie_fighter import TieFighter
from time import sleep
from .settings import Settings
from ..components.scoreboard import Scoreboard
from ..components.button import Button
from ..components.ship import Ship
from .game_stats import GameStats


def check_events(ai_settings, screen, stats, sb,play_button, ship, fighters, bullets):
    """Respond to keypresses and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb,play_button, ship,
                              fighters, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats,sb, play_button, ship,
                      fighters, bullets, mouse_x, mouse_y):
    """Start a new game when the player clicks Play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()
        pygame.mouse.set_visible(False)
        # Reset the game statistics.
        stats.reset_stats()
        stats.game_active = True

        #Reset the scoreboard images.
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # Empty the list of fighters and bullets.
        fighters.empty()
        bullets.empty()

        # Create a new fleet and center the ship
        create_fleet(ai_settings, screen, ship, fighters)
        ship.center_ship()


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """Respond to keypresses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet if limit not reached yet."""
    # Create a new bullet and add it to the bullets group.
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keyup_events(event, ship):
    """Respond to key releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def update_screen(ai_settings, screen, stats, sb, ship,
                  fighters, bullets, play_button):
    """Update images on the screen and flip to the new screen."""
    # Redraw the screen during each pass through the loop.
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    fighters.draw(screen)
    sb.show_score()
    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, fighters, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions
    bullets.update()
    # Get rid of bullets that have disappeared.
    for bullet in bullets.copy():
        if(bullet.rect.bottom <= 0):
            bullets.remove(bullet)

    check_bullet_fighter_collisions(
        ai_settings, screen, stats, sb, ship, fighters, bullets)


def check_bullet_fighter_collisions(ai_settings, screen, stats, sb, ship, fighters, bullets):
    """Respond to bullet-fighter collisions."""
    # Remove any bullets and fighter that collided.
    collisions = pygame.sprite.groupcollide(bullets, fighters, True, True)
    if collisions:
        for fighters in collisions.values():
            sb.stats.score += ai_settings.fighter_points*len(fighters)
            sb.prep_score()
        check_high_score(stats,sb)

    if len(fighters) == 0:
        # Destroy existing bullets and create a new fleet.
        bullets.empty()
        ai_settings.increase_speed()
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings, screen, ship, fighters)

def check_high_score(stats,sb):
    """Check to see if there's a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()

def create_fleet(ai_settings, screen, ship, fighters):
    """Create a full fleet of fighters."""
    # Create an fighter and find the number of fighters in a row.
    # Spacing between each fighter is equal to one fighter width
    fighter = TieFighter(ai_settings, screen)
    number_fighters_x = get_number_fighter_x(ai_settings, fighter.rect.width)
    number_rows = get_number_rows(
        ai_settings, ship.rect.height, fighter.rect.height)
    # Create the first row of fighters.
    for row_number in range(number_rows):
        for fighter_number in range(number_fighters_x):
            # Create an fighter and place it in the row.
            create_fighter(ai_settings, screen, fighters, fighter_number, row_number)


def get_number_fighter_x(ai_settings, fighter_width):
    """Determine the number of fighters that fit in a row."""
    available_space_x = ai_settings.screen_width - 2 * fighter_width
    number_fighters_x = int(available_space_x/(2*fighter_width))
    return number_fighters_x


def get_number_rows(ai_settings, ship_height, fighter_height):
    """Determine the number of rows of fighters that fit on the screen."""
    available_space_y = (ai_settings.screen_height -
                         (3*fighter_height) - ship_height)
    number_rows = int(available_space_y/(2*fighter_height))
    return number_rows


def create_fighter(ai_settings, screen, fighters, fighter_number, row_number):
    """Create an fighter and place it in the row."""
    fighter = TieFighter(ai_settings, screen)
    fighter_width = fighter.rect.width
    fighter.x = fighter_width + 2 * fighter_width * fighter_number
    fighter.rect.x = fighter.x
    fighter.rect.y = fighter.rect.height + 2*fighter.rect.height*row_number
    fighters.add(fighter)


def update_fighters(ai_settings, screen, stats, sb, ship, fighters, bullets):
    """Update the position of all fighters in the fleet."""
    check_fleet_edges(ai_settings, fighters)
    fighters.update()

    # Look for fighter-ship collisions.
    if pygame.sprite.spritecollideany(ship, fighters):
        ship_hit(ai_settings, screen, stats, sb, ship, fighters, bullets)
    check_fighter_bottom(ai_settings, screen, stats, sb, ship, fighters, bullets)


def check_fleet_edges(ai_settings, fighters):
    """Respond appropriately if any fighters have reached an edge."""
    for fighter in fighters.sprites():
        if fighter.check_edges():
            change_fleet_direction(ai_settings, fighters)
            break


def change_fleet_direction(ai_settings, fighters):
    """Drop the entire fleet and change the fleet's direction."""
    for fighter in fighters.sprites():
        fighter.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, screen, stats, sb, ship, fighters, bullets):
    """Respond to ship being hit by fighter."""
    # Decrement ships_left
    if stats.ships_left > 0:
        stats.ships_left -= 1

        # Empty the list of fighters and bullets.
        fighters.empty()
        bullets.empty()

        # Create a new fleet and center the ship.
        create_fleet(ai_settings, screen, ship, fighters)
        ship.center_ship()
        sb.prep_ships()
        # Pause.
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_fighter_bottom(ai_settings, screen, stats, sb, ship, fighters, bullets):
    """Check if any fighter has reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for fighter in fighters.sprites():
        if fighter.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship got hit.
            ship_hit(ai_settings, screen, stats, sb, ship, fighters, bullets)
            break

def run_game():
    # Initialize game and create a screen object.
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height))

    # Maka a ship , a group of bullets, and a group of fighters.
    ship = Ship(ai_settings, screen)
    bullets = Group()
    fighters = Group()

    # Create an instance to store game statistics.
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)
    # create a fleet of fighters.
    create_fleet(ai_settings, screen, ship, fighters)
    pygame.display.set_caption("The Empire Strikes Back")
    bg_color = (230, 230, 230)
    # Make the Play button.
    play_button = Button(ai_settings, screen, "Play")
    # Start the main loop for the game.
    while True:
        check_events(ai_settings, screen, stats,sb,
                        play_button, ship, fighters, bullets)
        if stats.game_active:
            ship.update()
            update_bullets(ai_settings, screen, stats,
                              sb, ship, fighters, bullets)
            update_fighters(ai_settings, screen, stats, sb, ship, fighters, bullets)
        update_screen(ai_settings, screen, stats, sb, ship,
                         fighters, bullets, play_button)