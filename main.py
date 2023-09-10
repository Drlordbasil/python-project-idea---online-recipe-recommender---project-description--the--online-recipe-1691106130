import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Recipe:
    def __init__(self, name, ingredients, instructions, cooking_time, difficulty_level):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.cooking_time = cooking_time
        self.difficulty_level = difficulty_level


class RecipeScraper:
    def __init__(self, url):
        self.url = url

    def scrape_recipe(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        recipe_name = soup.find("h1").text.strip()
        ingredients = [ingredient.text.strip()
                       for ingredient in soup.find_all("li", class_="ingredient")]
        instructions = [step.text.strip()
                        for step in soup.find_all("li", class_="instruction")]
        cooking_time = soup.find("span", class_="cooking-time").text.strip()
        difficulty_level = soup.find(
            "span", class_="difficulty-level").text.strip()
        recipe = Recipe(recipe_name, ingredients, instructions,
                        cooking_time, difficulty_level)
        return recipe


class RecipeRecommender:
    def __init__(self, recipes):
        self.recipes = recipes
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.recipe_matrix, self.recipe_names = self.build_recipe_matrix()

    def build_recipe_matrix(self):
        recipe_names = [recipe.name for recipe in self.recipes]
        ingredients_list = [' '.join(recipe.ingredients)
                            for recipe in self.recipes]
        recipe_matrix = self.vectorizer.fit_transform(ingredients_list)
        return recipe_matrix, recipe_names

    def recommend_recipes(self, user_ingredients):
        user_input_vector = self.vectorizer.transform(user_ingredients)
        similarity_scores = cosine_similarity(
            user_input_vector, self.recipe_matrix)
        top_recipe_indices = similarity_scores.argsort().flatten()[::-1][:5]
        recommendations = [self.recipe_names[i] for i in top_recipe_indices]
        return recommendations


class UserInterface:
    def __init__(self):
        self.recipes = []
        self.recipe_recommender = None

    def load_recipes(self):
        recipe_urls = [
            "https://www.example.com/recipe1",
            "https://www.example.com/recipe2",
            "https://www.example.com/recipe3"
        ]

        for url in recipe_urls:
            scraper = RecipeScraper(url)
            recipe = scraper.scrape_recipe()
            self.recipes.append(recipe)

        self.recipe_recommender = RecipeRecommender(self.recipes)

    def get_user_input(self):
        print("Welcome to the Online Recipe Recommender!")
        print("Please enter your dietary preferences, separated by commas:")
        dietary_preferences = input().split(",")

        print("Enter the ingredients you have on hand, separated by commas:")
        user_ingredients = input().split(",")

        return dietary_preferences, user_ingredients

    def run_recommendation(self):
        dietary_preferences, user_ingredients = self.get_user_input()
        recommendations = self.recipe_recommender.recommend_recipes(
            user_ingredients)

        print("Here are some recipe recommendations for you based on your input:\n")
        for recommendation in recommendations:
            print(recommendation)


if __name__ == "__main__":
    ui = UserInterface()
    ui.load_recipes()
    ui.run_recommendation()
