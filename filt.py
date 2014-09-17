class PromotionFilter():
    def __init__(self, promotion):
        self.promotion = promotion

    def generate_text(self, t):
        text = ""
        for title, info in t.items():
            if info['promotion'] in self.promotion:
                text += info['link'] + '\n'
                text += info['promotion'] + '\n'
                text += info['size'] + '\n'
                text += '=' * 50 + '\n' *2
        return text
