import pygame
import random
import json
import bisect

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE, BLACK, RED, GREEN, BLUE, NAVY = (255, 255, 255), (0, 0, 0), (178, 34, 34), (0, 200, 0), (0, 0, 255), (15, 23, 42)
BACKGROUND_COLOUR = NAVY

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flashcard Quiz")

objects = []

class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = pygame.font.SysFont('Arial', 40).render(buttonText, True, (20, 20, 20))

        objects.append(self)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


def get_leaderboard():
    with open('leaderboard.txt', 'r') as f:
        score = f.read()
        return score

def key_fn(t):
    return float(t[1])

def add_leaderboard(name, score):
    sorted_leaderboard = get_sorted_leaderboard_list()
    index = bisect.bisect(sorted_leaderboard, float(score), key=key_fn)
    sorted_leaderboard.insert(index, (name, score))
    res = ""
    for i, e in enumerate(sorted_leaderboard[:-1]):
        res += f"{e[0]}:{e[1]}"
        if i < 4:
            res += "\n"
    with open('leaderboard.txt', 'w') as f:
        f.write(res)

def get_sorted_leaderboard_list():
    leaderboard = get_leaderboard()
    res = []
    for i in leaderboard.split("\n"):
        name = i.split(":")[0]
        score = i.split(":")[1]
        res.append((name, score))
    return sorted(res, key=lambda x: float(x[1]))


def is_highscore(item):
    sorted_leaderboard = get_sorted_leaderboard_list()
    index = bisect.bisect(sorted_leaderboard, float(item[1]), key=key_fn)
    return index < 5



def draw_text(text, x, y, color=BLACK, font_size=20):
    render = pygame.font.Font(pygame.font.match_font('SFNS Mono'), font_size).render(text, True, color)
    screen.blit(render, (x, y))


def draw_flashcard_content(screen, x_offset, question, question_index, total_questions, elapsed_sec, user_input):
    inf, tense, pronoun, answer = question
    draw_text(inf, x_offset + 20, 170, (135, 206, 250), 25)
    draw_text(f"{tense}", x_offset + 20, 222, WHITE)
    draw_text(f"{pronoun} -> {user_input}", x_offset + 20, 270, WHITE)
    draw_text(f"Card: {question_index + 1}/{total_questions}", x_offset + 360, 170, WHITE, 18)
    if elapsed_sec:
        draw_text(f"{round(elapsed_sec, 2)}s", x_offset + 362, 220, WHITE, 18)


def animate_flashcard():
    for _ in range(2):
        pygame.draw.rect(screen, GREEN, (150, 150, 500, 250), 5, 25)
        pygame.display.flip()
        pygame.time.delay(150)
        pygame.draw.rect(screen, (144, 213, 255), (150, 150, 500, 250), 5, 25)
        pygame.display.flip()
        pygame.time.delay(150)


def animate_flashcard_wrong():
    pygame.draw.rect(screen, RED, (150, 150, 500, 250), 5, 25)
    pygame.display.flip()
    pygame.time.delay(100)
    pygame.draw.rect(screen, (255, 0, 0), (150, 150, 500, 250), 5, 25)
    pygame.display.flip()
    pygame.time.delay(100)


def slide_flashcard_out_in(old_q, new_q, question_index, total_questions, elapsed_sec, user_input, slide_direction):
    flashcard_rect = pygame.Rect(150, 150, 500, 250)
    clock = pygame.time.Clock()
    steps = 10
    dx = flashcard_rect.width // steps

    for i in range(steps + 1):
        screen.fill(BACKGROUND_COLOUR)

        offset = i * dx
        if slide_direction == "right":
            old_x = flashcard_rect.x + offset
            new_x = flashcard_rect.x - (flashcard_rect.width - offset)
        else:
            old_x = flashcard_rect.x - offset
            new_x = flashcard_rect.x + (flashcard_rect.width - offset)

        if i < steps:
            pygame.draw.rect(screen, (112, 128, 144), (old_x, 150, 500, 250), 0, 25)
            pygame.draw.rect(screen, (54, 69, 79), (old_x, 150, 500, 250), 5, 25)
            draw_flashcard_content(screen, old_x, old_q, question_index, total_questions, elapsed_sec, user_input)

        if i > 0:
            pygame.draw.rect(screen, (112, 128, 144), (new_x, 150, 500, 250), 0, 25)
            pygame.draw.rect(screen, (54, 69, 79), (new_x, 150, 500, 250), 5, 25)
            draw_flashcard_content(screen, new_x, new_q, question_index + 1, total_questions, elapsed_sec, "")

        pygame.display.flip()
        clock.tick(60)



def countdown_animation():
    font = pygame.font.Font(pygame.font.match_font('SFNS Mono'), 100)
    clock = pygame.time.Clock()

    for num in ["3", "2", "1", "Start"]:
        start_time = pygame.time.get_ticks()
        alpha_surface = pygame.Surface((WIDTH, HEIGHT))
        alpha_surface.fill(BACKGROUND_COLOUR)
        text = font.render(num, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        while pygame.time.get_ticks() - start_time < 600:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            alpha = 255 - int((pygame.time.get_ticks() - start_time) / 1000 * 255)
            alpha = max(0, min(255, alpha))
            alpha_surface.set_alpha(255 - alpha)

            screen.fill((15, 23, 42))
            screen.blit(text, text_rect)
            screen.blit(alpha_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)


def start_menu():
    running = True
    clock = pygame.time.Clock()

    # Timer variables for blinking
    blink_timer = 0
    show_text = True
    blink_interval = 500  # Blink interval in milliseconds

    while running:
        screen.fill(BACKGROUND_COLOUR)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False

        # Blink logic
        blink_timer += clock.get_time()
        if blink_timer >= blink_interval:
            show_text = not show_text
            blink_timer = 0

        text = pygame.font.Font(pygame.font.match_font('SFNS Mono'), 55).render("Spanish Conjugations", True, WHITE)
        screen.blit(text, (60, (HEIGHT // 2) - 100))

        # Display text if `show_text` is True
        if show_text:
            text2 = pygame.font.Font(pygame.font.match_font('SFNS Mono'), 30).render("Press any key to start", True, WHITE)
            screen.blit(text2, (190, (HEIGHT // 2 + 20)))

        # Update the display
        pygame.display.flip()

        # Delay to manage frame rate
        clock.tick(60)


def leaderboard_screen(new_highscore=False):
    running = True
    clock = pygame.time.Clock()

    # Timer variables for blinking
    blink_timer = 0
    show_text = True
    blink_interval = 500  # Blink interval in milliseconds
    font = pygame.font.Font(pygame.font.match_font('SFNS Mono'), 35)

    while running:
        screen.fill(BACKGROUND_COLOUR)

        # Blink logic
        blink_timer += clock.get_time()
        if blink_timer >= blink_interval:
            show_text = not show_text
            blink_timer = 0

        sorted_lb = get_sorted_leaderboard_list()
        screen.blit(font.render(f"Top 5 Leaderboard", True, GREEN), (40, 80))
        screen.blit(font.render(f"(R)estart, (Q)uit", True, WHITE), (40, 500))
        if not new_highscore:
            # NON FLASHING TEXT
            for i, e in enumerate(sorted_lb):
                screen.blit(font.render(f"{i + 1}) {e[0]}", True, WHITE), (70, 150 + i*60))
                screen.blit(font.render(f"{e[1]}s", True, WHITE), (600, 150 + i * 60))
        else:
            index = 0
            for i, e in enumerate(sorted_lb):
                if e[0] != new_highscore[0] or e[1] != str(new_highscore[1]):
                    screen.blit(font.render(f"{i + 1}) {e[0]}", True, WHITE), (70, 150 + i * 60))
                    screen.blit(font.render(f"{e[1]}s", True, WHITE), (600, 150 + i * 60))
                else:
                    index = i
            # FLASHING PORTION
            if show_text:
                text1 = font.render(f"{index + 1}) {new_highscore[0]}", True, WHITE)
                text2 = font.render(f"{new_highscore[1]}s", True, WHITE)
                screen.blit(text1, (70, 150 + index * 60))
                screen.blit(text2, (600, 150 + index * 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB or event.key == pygame.K_r:
                    game_loop()
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()

        pygame.display.flip()
        clock.tick(60)


def generate_questions(num_questions):
    with open('spanish_conjugations.json', 'r') as f:
        verbs = json.load(f)

    infinitives = list(verbs.keys())
    tenses = ["preterite", "present", "subjunctive", "imperfect"]
    pronouns = ["yo", "tú", "él/ella", "nosotros", "ellos/Uds"]

    selected_questions = []
    for i in range(num_questions):
        inf = random.choice(infinitives)
        tense = random.choice(tenses)
        pronoun = random.choice(pronouns)
        selected_questions.append([inf, tense, pronoun, verbs[inf][tense][pronoun]])

    return selected_questions


def game_loop(mistakes=False):
    total_questions = 10

    running = True
    question_index = 0
    user_input = ""
    score = 0
    show_correct = False
    show_correct_text = False
    correct_answer = ""
    game_over = False
    text_color = WHITE
    just_popped_mistakes = False
    highscore = False
    if not mistakes:
        mistakes = []
        selected_questions = generate_questions(total_questions)
        review_mistakes_mode = False
        countdown_animation()
    else:
        selected_questions = mistakes
        num_mistakes = len(selected_questions)
        review_mistakes_mode = True



    start_time = pygame.time.get_ticks()
    timer_active = True
    final_time = 0

    while running:
        screen.fill(BACKGROUND_COLOUR)

        current_ticks = pygame.time.get_ticks()
        elapsed_ms = current_ticks - start_time
        elapsed_sec = elapsed_ms / 1000.0

        pygame.draw.rect(screen, (112, 128, 144), (150, 150, 500, 250), 0, 25)
        pygame.draw.rect(screen, (54, 69, 79), (150, 150, 500, 250), 5, 25)

        if game_over:
            if not review_mistakes_mode:
                draw_text(f"Game Over! Your Score: {score}/{len(selected_questions)} -> {int((score/len(selected_questions))*100)}%", 170, 170, text_color)
                if score == 10 and is_highscore(('', final_time)):
                    highscore = True
                    draw_text(f"Highscore! {final_time}s", 170, 220, GREEN)
                    draw_text(f"Enter your name for the leaderboard:", 170, 270, text_color)
                    draw_text(f"{user_input}", 170, 320, text_color)

                    #add_leaderboard(name, final_time)
                    pass
                else:
                    if len(mistakes) > 0:
                        draw_text(f"Time: {final_time}s", 170, 245, text_color)
                        draw_text(f"(R)eplay, (Q)uit, (L)eaderboard", 170, 310, text_color)
                        draw_text(f"(P)ractice {len(mistakes)} mistakes", 170, 350, text_color)
                    else:
                        draw_text(f"Time: {final_time}s", 170, 220, text_color)
                        draw_text(f"Average time per verb: {round(final_time/len(selected_questions), 2)}s", 170, 270, text_color)
                        draw_text(f"(R)eplay, (Q)uit, (L)eaderboard", 170, 320, text_color)

            else:
                draw_text(f"Good job!", 170, 170, text_color)
                draw_text(f"You've reviewed {num_mistakes} verbs", 170, 245, text_color)
                draw_text(f"R to Replay, Q to Quit", 170, 320, text_color)
        else:
            if timer_active:
                display_time = elapsed_sec
            else:
                display_time = final_time

            if not review_mistakes_mode:
                draw_flashcard_content(screen, 150, selected_questions[question_index], question_index, len(selected_questions), display_time, user_input)
            else:
                if mistakes:
                    if not just_popped_mistakes:
                        draw_flashcard_content(screen, 150, mistakes[question_index], question_index, num_mistakes, False, user_input)
                    else:
                        draw_flashcard_content(screen, 150, last_mistake, question_index, num_mistakes, False, user_input)
                else:
                    draw_flashcard_content(screen, 150, last_mistake, question_index, num_mistakes, False, user_input)


            if show_correct_text:
                draw_text("Correct!", 350, 320, GREEN)
                draw_text("Press Enter to continue...", 260, 350, text_color)
            elif show_correct:
                draw_text(f'Correct answer: "{correct_answer}"', 170, 320, RED)
                draw_text("Press Enter to continue...", 260, 350, text_color)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    game_loop()
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over:
                    if not highscore:
                        if event.key == pygame.K_r:
                            game_loop()
                        elif event.key == pygame.K_p:
                            game_loop(mistakes)
                        elif event.key == pygame.K_q:
                            running = False
                        elif event.key == pygame.K_l:
                            leaderboard_screen()
                    else:
                        if event.key == pygame.K_RETURN and len(user_input.strip()) > 0:
                            highscore = False
                            add_leaderboard(user_input, final_time)
                            leaderboard_screen((user_input, final_time))
                        elif event.key == pygame.K_BACKSPACE:
                            user_input = user_input[:-1]
                        else:
                            user_input += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        if question_index + 1 >= total_questions:
                            if timer_active:
                                final_time = round(elapsed_sec, 2)
                                timer_active = False
                        if show_correct or show_correct_text:
                            just_popped_mistakes = False
                            if show_correct:
                                slide_direction = "left"
                            else:
                                slide_direction = "right"

                            if question_index + 1 < len(selected_questions):
                                slide_flashcard_out_in(
                                    selected_questions[question_index],
                                    selected_questions[question_index + 1],
                                    question_index,
                                    total_questions,
                                    elapsed_sec,
                                    user_input,
                                    slide_direction
                                )
                            if review_mistakes_mode and question_index < len(selected_questions):
                                question_index += 1

                            if not review_mistakes_mode:
                                question_index += 1
                            user_input = ""
                            show_correct = False
                            show_correct_text = False
                            if not review_mistakes_mode:
                                if question_index >= total_questions:
                                    game_over = True
                            else:
                                if not mistakes:
                                    game_over = True
                        else:
                            if not review_mistakes_mode:
                                inf, tense, pronoun, answer = selected_questions[question_index]
                            else:
                                inf, tense, pronoun, answer = mistakes[question_index]

                            # CORRECT ANSWER
                            if user_input.lower().strip() == answer.lower():
                                show_correct_text = True
                                if not review_mistakes_mode:
                                    score += 1
                                else:
                                    last_mistake = mistakes.pop(question_index)
                                    just_popped_mistakes = True
                                animate_flashcard()
                                if not review_mistakes_mode:
                                    if question_index + 1 < len(selected_questions):
                                        slide_flashcard_out_in(
                                            selected_questions[question_index],
                                            selected_questions[question_index + 1],
                                            question_index,
                                            total_questions,
                                            elapsed_sec,
                                            user_input,
                                            "right")

                                    question_index += 1
                                    user_input = ""
                                    show_correct = False
                                    show_correct_text = False
                                    if question_index >= total_questions:
                                        game_over = True
                            # NO ANSWER
                            elif len(user_input.strip()) == 0:
                                animate_flashcard_wrong()

                            # WRONG ANSWER
                            else:
                                correct_answer = answer
                                show_correct = True
                                if not review_mistakes_mode and selected_questions[question_index] not in mistakes:
                                    mistakes.append(selected_questions[question_index])
                                else:
                                    just_popped_mistakes = False

                                animate_flashcard_wrong()
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode

        if review_mistakes_mode and question_index >= len(mistakes):
            question_index = 0

        for object in objects:
            object.process()

        pygame.display.flip()
    pygame.quit()


start_menu()
game_loop()
