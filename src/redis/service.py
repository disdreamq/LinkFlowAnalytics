from src.modules.click.schemas import SClickResponse


def get_increments_for_links(clicks: list[SClickResponse]) -> dict[int, int]:
    link_ids = {}

    for click in clicks:
        link_ids[click.link_id] = link_ids.get(click.link_id, 0) + 1
        
    return link_ids