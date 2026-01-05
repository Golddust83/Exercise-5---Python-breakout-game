def clamp(value, low, high):
    return max(low, min(high, value))


def reflect_ball_on_rect(ball_rect, vel, obstacle_rect):
    """
    Reflect velocity based on which side is hit more
    """
    vx, vy = vel
    overlap_left = ball_rect.right - obstacle_rect.left
    overlap_right = obstacle_rect.right - ball_rect.left
    overlap_top = ball_rect.bottom - obstacle_rect.top
    overlap_bottom = obstacle_rect.bottom - ball_rect.top

    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

    if min_overlap == overlap_left:
        ball_rect.right = obstacle_rect.left
        vx = -abs(vx)
    elif min_overlap == overlap_right:
        ball_rect.left = obstacle_rect.right
        vx = abs(vx)
    elif min_overlap == overlap_top:
        ball_rect.bottom = obstacle_rect.top
        vy = -abs(vy)
    else:
        ball_rect.top = obstacle_rect.bottom
        vy = abs(vy)

    return (vx, vy)